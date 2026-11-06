"""
Module 2: ID-Conditioned Recurrent LIF Spiking Neural Network (SNN) with True k-WTA lateral inhibition.
"""

import time
from typing import Tuple, List
import numpy as np
import torch
import torch.nn as nn

from .config import (
    CS_INPUT_DIM,
    CS_HIDDEN_DIM,
    CS_PRED_DIM,
    CS_K_WTA,
    CS_V_TH,
    CS_V_CEIL,
)
from .data_loader import CANFrame
from .encoder import PerIDNeuromorphicEncoder


class SuperSpikeSurrogate(torch.autograd.Function):
    @staticmethod
    def forward(ctx, v_excess):
        ctx.save_for_backward(v_excess)
        return (v_excess > 0.0).float()

    @staticmethod
    def backward(ctx, grad_output):
        v_excess, = ctx.saved_tensors
        gamma_sigma = 10.0
        grad = grad_output / ((gamma_sigma * torch.abs(v_excess) + 1.0) ** 2)
        return grad


class IDConditionedKWtaSNN(nn.Module):
    """
    Module 2: ID-Conditioned Recurrent LIF Spiking Neural Network
    - True hardware-enforced k-WTA lateral inhibition (K_max = 12)
    - Conditioned next-frame predictive readout: p_pred = sigmoid(W_rec * s_hid + W_id * s_id)
    - Physics-informed Somatic Excursion (MES) penalty
    """
    def __init__(
        self,
        input_dim: int = CS_INPUT_DIM,
        hidden_dim: int = CS_HIDDEN_DIM,
        pred_dim: int = CS_PRED_DIM,
        k_wta: int = CS_K_WTA,
        v_th: float = CS_V_TH,
        v_ceil: float = CS_V_CEIL
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.pred_dim = pred_dim
        self.k_wta = k_wta
        self.v_th = v_th
        self.v_ceil = v_ceil

        self.fc_in = nn.Linear(input_dim, hidden_dim, bias=False)
        self.fc_rec = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.fc_pred_rec = nn.Linear(hidden_dim, pred_dim, bias=False)
        self.fc_pred_id = nn.Linear(11, pred_dim, bias=False)

        self.beta_raw = nn.Parameter(torch.full((hidden_dim,), 1.75))

        nn.init.xavier_uniform_(self.fc_in.weight, gain=0.6)
        nn.init.orthogonal_(self.fc_rec.weight, gain=0.3)
        nn.init.xavier_uniform_(self.fc_pred_rec.weight, gain=0.5)
        nn.init.xavier_uniform_(self.fc_pred_id.weight, gain=0.5)

    def get_beta(self) -> torch.Tensor:
        return 0.50 + 0.48 * torch.sigmoid(self.beta_raw)

    def forward_step(
        self,
        s_in: torch.Tensor,
        v_hid_prev: torch.Tensor,
        s_hid_prev: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, int]:
        beta = self.get_beta()

        # 1. Predictive Readout Conditioned on Arbitration ID
        s_id = s_in[:, :11]
        p_logits = self.fc_pred_rec(s_hid_prev) + self.fc_pred_id(s_id)
        pred_probs = torch.sigmoid(p_logits)

        # 2. Somatic Integration
        i_syn = self.fc_in(s_in) + self.fc_rec(s_hid_prev)
        v_pre = beta * v_hid_prev + i_syn

        # 3. True k-WTA Lateral Inhibition
        v_excess = v_pre - self.v_th
        raw_spikes = SuperSpikeSurrogate.apply(v_excess)

        if self.k_wta < self.hidden_dim:
            _, topk_indices = torch.topk(v_pre, self.k_wta, dim=-1)
            k_wta_mask = torch.zeros_like(raw_spikes).scatter_(-1, topk_indices, 1.0)
            s_hid = raw_spikes * k_wta_mask
        else:
            s_hid = raw_spikes

        # 4. Soft Reset & Voltage Clamp
        v_next = torch.where(
            s_hid > 0.0,
            v_pre - self.v_th,
            torch.clamp(v_pre, max=self.v_ceil)
        )

        # 5. Physics-Informed Somatic Excursion (MES)
        mes_score = torch.relu(v_pre - self.v_th).mean(dim=-1)

        # Exact Synaptic Operations (ACs)
        active_in = int(s_in.sum().item())
        active_rec_prev = int(s_hid_prev.sum().item())
        active_hid = int(s_hid.sum().item())
        exact_acs = (active_in * self.hidden_dim) + (active_rec_prev * self.hidden_dim) + (active_hid * self.pred_dim)

        return pred_probs, v_next, s_hid, mes_score, exact_acs


def pretrain_conformal_spike(
    model: IDConditionedKWtaSNN,
    encoder: PerIDNeuromorphicEncoder,
    benign_frames: List[CANFrame],
    epochs: int = 2,
    seq_len: int = 50,
    lr: float = 0.005,
    device: str = "cpu"
) -> IDConditionedKWtaSNN:
    print(f"\n[Pretraining] Starting Self-Supervised T-BPTT on {len(benign_frames):,} benign frames ({epochs} epochs)...", flush=True)
    t0 = time.time()

    encoder.reset_state()
    x_list, tgt_list = [], []
    for f in benign_frames:
        s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
        x_list.append(s_in)
        tgt_list.append(tgt)

    x_arr = np.array(x_list, dtype=np.float32)
    tgt_arr = np.array(tgt_list, dtype=np.float32)

    num_chunks = len(x_arr) // seq_len
    x_tensor = torch.from_numpy(x_arr[:num_chunks * seq_len]).to(device)
    tgt_tensor = torch.from_numpy(tgt_arr[:num_chunks * seq_len]).to(device)

    model = model.to(device)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    bce = nn.BCELoss(reduction='none')

    for ep in range(epochs):
        v_h = torch.zeros(1, model.hidden_dim, device=device)
        s_h = torch.zeros(1, model.hidden_dim, device=device)
        ep_loss = 0.0

        for c in range(num_chunks):
            optimizer.zero_grad()
            c_x = x_tensor[c * seq_len:(c + 1) * seq_len]
            c_tgt = tgt_tensor[c * seq_len:(c + 1) * seq_len]

            chunk_loss = 0.0
            for t in range(seq_len):
                p_prob, v_h, s_h, _, _ = model.forward_step(c_x[t:t + 1], v_h, s_h)
                raw_bce = bce(p_prob, c_tgt[t:t + 1])
                chunk_loss = chunk_loss + raw_bce.mean()

            chunk_loss = chunk_loss / seq_len + 0.001 * s_h.mean()
            chunk_loss.backward()
            optimizer.step()

            ep_loss += chunk_loss.item()
            v_h = v_h.detach()
            s_h = s_h.detach()

        avg_loss = ep_loss / num_chunks
        print(f"  Epoch {ep + 1}/{epochs} - Average T-BPTT Loss: {avg_loss:.4f}", flush=True)

    print(f"[Pretraining Complete] Finished in {time.time() - t0:.2f} s", flush=True)
    model.eval()
    return model


def compute_frame_score(
    model: IDConditionedKWtaSNN,
    s_in: np.ndarray,
    v_hid: torch.Tensor,
    s_hid: torch.Tensor,
    dense_id: int,
    encoder: PerIDNeuromorphicEncoder
) -> Tuple[float, torch.Tensor, torch.Tensor, int]:
    s_in_t = torch.from_numpy(s_in).unsqueeze(0).float()
    with torch.no_grad():
        p_prob, v_next, s_next, mes_score, exact_acs = model.forward_step(s_in_t, v_hid, s_hid)

    p_np = p_prob.squeeze(0).numpy()
    tgt_np = s_in[11:43]
    w_vec = np.ones(32, dtype=np.float32)
    for j in range(8):
        w = encoder.w_byte[dense_id, j]
        w_vec[2 * j] = w
        w_vec[2 * j + 1] = w
        w_vec[16 + j] = 2.0 * w

    l1_err = float(np.sum(w_vec * np.abs(tgt_np - p_np)) / 32.0)
    mag_shock = 0.35 * float(np.sum(tgt_np[16:24]))
    mes = float(mes_score.item())

    # Timing flood shock on compressed arrival of periodic/high-priority arbitration IDs (e.g. DoS 0x000)
    cid_val = encoder.dense_to_can_id[dense_id] if dense_id < len(encoder.dense_to_can_id) else 0x100
    timing_shock = 0.85 if (tgt_np[24] >= 1.0 and (cid_val == 0x000 or cid_val < 0x100)) else 0.0

    asil_w = encoder.get_asil_weight(cid_val)
    total_score = float(np.clip(asil_w * (l1_err + mag_shock + timing_shock + 0.20 * mes), 0.0, 3.0))
    return total_score, v_next, s_next, exact_acs
