"""
Embedded Baselines and Comparative IDS Paradigms:
  - INT8 Tiny-MLP Autoencoder
  - INT8 Micro-GRU
  - Statistical/Timing-Entropy IDS (Moore et al.)
  - Heuristic Static Threshold (mu + 3*sigma)
  - Split Conformal Prediction (Massaad et al.)
  - Unguarded Online ACI (Gibbs & Candes)
  - Alert-Gated Online ACI (Skip on Alert)
  - Non-Neural Delta + Conformal
"""

import math
import time
import collections
from typing import Dict, List, Tuple
import numpy as np
import torch
import torch.nn as nn

from .config import (
    CS_INPUT_DIM,
    CS_PRED_DIM,
    CS_WINDOW_W,
    ALPHA_TARGET,
    GAMMA_BASE,
)
from .data_loader import CANFrame
from .encoder import PerIDNeuromorphicEncoder
from .conformal import FenwickQuantileBuffer


class INT8TinyMLPAutoencoder(nn.Module):
    """Fair Embedded Baseline 1: 2-layer Tiny-MLP autoencoder (~3,500 INT8 MACs)"""
    def __init__(self, in_dim=CS_INPUT_DIM, hidden_dim=32, out_dim=CS_PRED_DIM):
        super().__init__()
        self.enc = nn.Linear(in_dim, hidden_dim)
        self.dec = nn.Linear(hidden_dim, out_dim)

    def forward(self, x):
        h = torch.relu(self.enc(x))
        return torch.sigmoid(self.dec(h))


class INT8MicroGRU(nn.Module):
    """Fair Embedded Baseline 2: 64-unit Micro-GRU (~18,000 INT8 MACs)"""
    def __init__(self, in_dim=CS_INPUT_DIM, hidden_dim=64, out_dim=CS_PRED_DIM):
        super().__init__()
        self.gru = nn.GRU(in_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, out_dim)

    def forward(self, x, h):
        out, h_next = self.gru(x, h)
        pred = torch.sigmoid(self.fc(out))
        return pred, h_next


def pretrain_baseline_models(
    mlp: INT8TinyMLPAutoencoder,
    gru: INT8MicroGRU,
    encoder: PerIDNeuromorphicEncoder,
    benign_frames: List[CANFrame],
    epochs: int = 2,
    lr: float = 0.005,
    device: str = "cpu"
) -> Tuple[INT8TinyMLPAutoencoder, INT8MicroGRU]:
    """Pretrains Tiny-MLP and Micro-GRU baselines on the same 100,000 benign frames."""
    print(f"\n[Baseline Pretraining] Training Tiny-MLP and Micro-GRU on {len(benign_frames):,} benign frames...", flush=True)
    t0 = time.time()
    encoder.reset_state()
    x_list, tgt_list = [], []
    for f in benign_frames[:50000]:  # 50k frames for rapid convergence
        s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
        x_list.append(s_in)
        tgt_list.append(tgt)

    x_tensor = torch.from_numpy(np.array(x_list, dtype=np.float32)).to(device)
    tgt_tensor = torch.from_numpy(np.array(tgt_list, dtype=np.float32)).to(device)

    mlp = mlp.to(device).train()
    gru = gru.to(device).train()
    opt_mlp = torch.optim.Adam(mlp.parameters(), lr=lr)
    opt_gru = torch.optim.Adam(gru.parameters(), lr=lr)
    bce = nn.BCELoss()

    batch_size = 64
    num_batches = len(x_tensor) // batch_size

    for ep in range(epochs):
        for b in range(num_batches):
            bx = x_tensor[b * batch_size:(b + 1) * batch_size]
            by = tgt_tensor[b * batch_size:(b + 1) * batch_size]

            # MLP update
            opt_mlp.zero_grad()
            p_mlp = mlp(bx)
            loss_mlp = bce(p_mlp, by)
            loss_mlp.backward()
            opt_mlp.step()

            # GRU update
            opt_gru.zero_grad()
            bx_seq = bx.unsqueeze(1)
            h0 = torch.zeros(1, batch_size, 64, device=device)
            p_gru, _ = gru(bx_seq, h0)
            loss_gru = bce(p_gru.squeeze(1), by)
            loss_gru.backward()
            opt_gru.step()

    mlp.eval()
    gru.eval()
    print(f"[Baseline Pretraining Complete] Finished in {time.time() - t0:.2f} s", flush=True)
    return mlp, gru


class StatisticalTimingEntropyIDS:
    """Fair Embedded Baseline 3: Inter-Arrival Time + Payload Entropy IDS (Moore et al.)"""
    def __init__(self):
        self.last_ts: Dict[int, float] = {}
        self.mean_dt: Dict[int, float] = {}
        self.var_dt: Dict[int, float] = {}

    def decide(self, ts: float, cid: int, payload: bytes) -> Tuple[int, float]:
        score = 0.0
        if cid in self.last_ts:
            dt = ts - self.last_ts[cid]
            m_dt = self.mean_dt.get(cid, dt)
            v_dt = self.var_dt.get(cid, 0.001 ** 2)
            z_dt = abs(dt - m_dt) / max(1e-5, math.sqrt(v_dt))
            self.mean_dt[cid] = 0.98 * m_dt + 0.02 * dt
            self.var_dt[cid] = 0.98 * v_dt + 0.02 * ((dt - m_dt) ** 2)

            counts = collections.Counter(payload)
            ent = -sum((c / 8.0) * math.log2(c / 8.0) for c in counts.values())
            score = z_dt + 0.5 * ent
        else:
            self.mean_dt[cid] = 0.010
            self.var_dt[cid] = 0.0001
        self.last_ts[cid] = ts
        decision = 1 if score > 3.5 else 0
        return decision, score


class HeuristicStaticIDS:
    """Method 1: Fixed Threshold (mu + 3*sigma)"""
    def __init__(self, cal_scores: np.ndarray):
        self.threshold = float(np.mean(cal_scores) + 3.0 * np.std(cal_scores))

    def decide(self, score: float) -> int:
        return 1 if score > self.threshold else 0


class SplitConformalIDS:
    """Method 2: Split Conformal Prediction (Massaad et al.)"""
    def __init__(self, cal_scores: np.ndarray, alpha_target: float = ALPHA_TARGET):
        self.alpha_target = alpha_target
        n = len(cal_scores)
        q_level = min(1.0, (1.0 - alpha_target) * (1.0 + 1.0 / n))
        self.threshold = float(np.quantile(cal_scores, q_level))

    def decide(self, score: float) -> int:
        return 1 if score > self.threshold else 0


class UnguardedOnlineACIIDS:
    """Method 3: Unguarded Online ACI (Gibbs & Candes, NeurIPS 2021)"""
    def __init__(self, cal_scores: np.ndarray, alpha_target: float = ALPHA_TARGET, gamma_base: float = GAMMA_BASE):
        self.alpha_target = alpha_target
        self.alpha_k = alpha_target
        self.gamma_base = gamma_base
        self.q_buffer = FenwickQuantileBuffer(capacity=CS_WINDOW_W)
        for s in cal_scores:
            self.q_buffer.push(float(s))

    def get_threshold(self) -> float:
        n = max(1, self.q_buffer.count)
        q_level = min(1.0, (1.0 - self.alpha_k) * (1.0 + 1.0 / n))
        return self.q_buffer.query_quantile(q_level)

    def decide(self, score: float) -> Tuple[int, float, float]:
        lambda_k = self.get_threshold()
        decision = 1 if score > lambda_k else 0
        err_k = 1.0 if decision == 1 else 0.0

        self.alpha_k = float(np.clip(
            self.alpha_k + self.gamma_base * (self.alpha_target - err_k),
            1e-4, 0.05
        ))
        self.q_buffer.push(score)
        return decision, lambda_k, self.alpha_k


class AlertGatedOnlineACIIDS:
    """Method 4 (Baseline): Alert-Gated ACI (Skips update on alert, but lacks staging & quarantine)"""
    def __init__(self, cal_scores: np.ndarray, alpha_target: float = ALPHA_TARGET, gamma_base: float = GAMMA_BASE):
        self.alpha_target = alpha_target
        self.alpha_k = alpha_target
        self.gamma_base = gamma_base
        self.q_buffer = FenwickQuantileBuffer(capacity=CS_WINDOW_W)
        for s in cal_scores:
            self.q_buffer.push(float(s))

    def get_threshold(self) -> float:
        n = max(1, self.q_buffer.count)
        q_level = min(1.0, (1.0 - self.alpha_k) * (1.0 + 1.0 / n))
        return self.q_buffer.query_quantile(q_level)

    def decide(self, score: float) -> Tuple[int, float, float]:
        lambda_k = self.get_threshold()
        decision = 1 if score > lambda_k else 0
        err_k = 1.0 if decision == 1 else 0.0

        self.alpha_k = float(np.clip(
            self.alpha_k + self.gamma_base * (self.alpha_target - err_k),
            1e-4, 0.05
        ))
        if decision == 0:
            self.q_buffer.push(score)
        return decision, lambda_k, self.alpha_k


class NonNeuralDeltaConformalIDS:
    """Method 5 (Baseline): Per-ID Delta Magnitude Check with Conformal Layer"""
    def __init__(self, cal_scores: np.ndarray, alpha_target: float = ALPHA_TARGET, gamma_base: float = GAMMA_BASE):
        self.alpha_target = alpha_target
        self.alpha_k = alpha_target
        self.gamma_base = gamma_base
        self.last_payload: Dict[int, bytes] = {}
        self.q_buffer = FenwickQuantileBuffer(capacity=CS_WINDOW_W)
        for s in cal_scores:
            self.q_buffer.push(float(s))

    def compute_score(self, can_id: int, payload: bytes) -> float:
        if can_id in self.last_payload:
            lp = self.last_payload[can_id]
            p_len = min(len(payload), len(lp), 8)
            if p_len > 0:
                diff = sum(abs(int(payload[j]) - int(lp[j])) for j in range(p_len)) / (p_len * 255.0)
            else:
                diff = 0.0
        else:
            diff = 0.0
        return float(diff * 3.0)

    def decide(self, can_id: int, payload: bytes) -> Tuple[int, float, float]:
        score = self.compute_score(can_id, payload)
        n = max(1, self.q_buffer.count)
        q_level = min(1.0, (1.0 - self.alpha_k) * (1.0 + 1.0 / n))
        lambda_k = self.q_buffer.query_quantile(q_level)
        decision = 1 if score > lambda_k else 0
        err_k = 1.0 if decision == 1 else 0.0

        self.alpha_k = float(np.clip(
            self.alpha_k + self.gamma_base * (self.alpha_target - err_k),
            1e-4, 0.05
        ))
        if decision == 0:
            self.last_payload[can_id] = payload
            self.q_buffer.push(score)
        return decision, lambda_k, self.alpha_k
