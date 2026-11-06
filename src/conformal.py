"""
Module 4: O(log M) Fenwick Quantile Buffer & Calibrated ConformalSpike IDS.
"""

import math
import collections
from typing import List, Tuple
import numpy as np

from .config import (
    CS_WINDOW_W,
    CS_FENWICK_BINS,
    ALPHA_TARGET,
    LAMBDA_RHO,
    RHO_THRESH,
    QUARANTINE_KAPPA,
    GAMMA_BASE,
    STAGING_QUEUE_LEN,
    CS_MAX_IDS,
    UPDATE_BLOCK_SIZE,
)


class FenwickQuantileBuffer:
    def __init__(self, capacity: int = CS_WINDOW_W, num_bins: int = CS_FENWICK_BINS):
        self.capacity = capacity
        self.num_bins = num_bins
        self.tree = np.zeros(num_bins + 1, dtype=np.int32)
        self.ring = np.zeros(capacity, dtype=np.int16)
        self.head = 0
        self.count = 0
        self.min_val = 0.0
        self.max_val = 3.0

    def val_to_bin(self, val: float) -> int:
        norm = (val - self.min_val) / (self.max_val - self.min_val)
        b = int(np.clip(round(norm * (self.num_bins - 1)), 0, self.num_bins - 1)) + 1
        return b

    def bin_to_val(self, b: int) -> float:
        norm = (b - 1) / (self.num_bins - 1)
        return float(self.min_val + norm * (self.max_val - self.min_val))

    def _fenwick_add(self, idx: int, delta: int):
        while idx <= self.num_bins:
            self.tree[idx] += delta
            idx += idx & (-idx)

    def _fenwick_find_rank(self, target_rank: int) -> int:
        idx = 0
        mask = 1024
        while mask > 0:
            next_idx = idx + mask
            if next_idx <= self.num_bins and self.tree[next_idx] < target_rank:
                idx = next_idx
                target_rank -= self.tree[idx]
            mask >>= 1
        return idx + 1

    def push(self, val: float):
        b = self.val_to_bin(val)
        if self.count == self.capacity:
            old_b = int(self.ring[self.head])
            self._fenwick_add(old_b, -1)
        else:
            self.count += 1
        self.ring[self.head] = b
        self._fenwick_add(b, 1)
        self.head = (self.head + 1) % self.capacity

    def query_quantile(self, q: float) -> float:
        if self.count == 0:
            return 0.5
        q_clamped = max(1e-4, min(1.0, q))
        target_rank = max(1, min(self.count, int(math.ceil(q_clamped * self.count))))
        b = self._fenwick_find_rank(target_rank)
        return self.bin_to_val(b)


class ConformalSpikeIDS:
    """
    Method 6: Proposed ConformalSpike (G-RW-CRC with Delayed Staging & Multi-Tiered Quarantine)
    Features:
      - 32-frame Delayed Staging Ring Buffer (L=32): pre-quarantine attack frames are purged
      - Per-ID alert density rho_id: distinguishes benign multi-ID shifts from targeted ECU attacks
      - Global alert density rho_global: detects systemic bus flooding attacks
      - Extreme kinematic shock gate: s_k > kappa * lambda_k (instant trigger on frame 1)
      - Principled quarantine recovery: clears when extreme shocks cease and alert densities decay
      - Block-based step size adaptation gamma_k: provably converges via Abel summation
    """
    def __init__(
        self,
        cal_scores: np.ndarray,
        alpha_target: float = ALPHA_TARGET,
        lambda_rho: float = LAMBDA_RHO,
        rho_thresh: float = RHO_THRESH,
        quarantine_kappa: float = QUARANTINE_KAPPA,
        gamma_base: float = GAMMA_BASE,
        staging_len: int = STAGING_QUEUE_LEN
    ):
        self.alpha_target = alpha_target
        self.alpha_k = alpha_target
        self.lambda_rho = lambda_rho
        self.rho_thresh = rho_thresh
        self.quarantine_kappa = quarantine_kappa
        self.gamma_base = gamma_base
        self.staging_len = staging_len

        self.q_buffer = FenwickQuantileBuffer(capacity=CS_WINDOW_W)
        for s in cal_scores:
            self.q_buffer.push(float(s))

        # Staging FIFO: (score, decision, lambda_k, is_quarantined)
        self.staging_queue: collections.deque = collections.deque()

        # Global and Per-ID alert density trackers
        self.alert_density_global = 0.0
        self.alert_density_id = np.zeros(CS_MAX_IDS, dtype=np.float32)

        # Block-based step size adaptation state
        self.frame_counter = 0
        self.current_gamma = gamma_base
        self.ema_mean = float(np.mean(cal_scores))
        self.ema_var = float(np.var(cal_scores) + 1e-5)
        self.block_scores: List[float] = []

    def get_threshold(self) -> float:
        n = max(1, self.q_buffer.count)
        q_level = min(1.0, (1.0 - self.alpha_k) * (1.0 + 1.0 / n))
        return self.q_buffer.query_quantile(q_level)

    def decide(self, score: float, dense_id: int, has_shock: bool = False) -> Tuple[int, float, float, bool, float, float]:
        lambda_k = self.get_threshold()
        decision = 1 if (score > lambda_k or has_shock) else 0

        # Update Leaky Alert Density Trackers
        self.alert_density_global = self.lambda_rho * self.alert_density_global + (1.0 - self.lambda_rho) * decision
        self.alert_density_id[dense_id] = self.lambda_rho * self.alert_density_id[dense_id] + (1.0 - self.lambda_rho) * decision

        # Gate 2: Multi-Tiered Quarantine Shield (Gate 1: Spatial/Magnitude Excursion Shock)
        extreme_shock = (score > self.quarantine_kappa * lambda_k) or has_shock
        ecu_concentrated = (self.alert_density_id[dense_id] > self.rho_thresh)
        bus_flooded = (self.alert_density_global > 0.35)
        is_quarantined = extreme_shock or ecu_concentrated or bus_flooded

        is_alert = 1 if (score > lambda_k or has_shock) else 0

        # Enqueue current frame into Delayed Staging Buffer
        self.staging_queue.append((score, is_alert, lambda_k, is_quarantined))

        if is_quarantined:
            # Mark all frames currently in staging buffer as quarantined so they cannot contaminate q_buffer
            self.staging_queue = collections.deque([
                (s, d, th, True) for (s, d, th, q) in self.staging_queue
            ])

        # If staging queue has reached capacity L=32, commit verified safe frame
        if len(self.staging_queue) >= self.staging_len:
            s_old, d_old, th_old, q_old = self.staging_queue.popleft()
            # Standard online Robbins-Monro ACI step
            err_k = 1.0 if d_old == 1 else 0.0
            self.alpha_k = float(np.clip(
                self.alpha_k + self.current_gamma * (self.alpha_target - err_k),
                0.001, 0.020
            ))
            # Sliding window quantile buffer only admits verified safe (unquarantined) frames
            if not q_old:
                self.q_buffer.push(s_old)

                # Block-based step size adaptation (every B=64 frames)
                self.block_scores.append(s_old)
                self.frame_counter += 1
                if self.frame_counter >= UPDATE_BLOCK_SIZE:
                    block_mean = float(np.mean(self.block_scores))
                    z_drift = abs(block_mean - self.ema_mean) / math.sqrt(self.ema_var + 1e-6)
                    self.current_gamma = self.gamma_base * (1.0 + 0.5 * min(z_drift, 4.0))

                    diff = block_mean - self.ema_mean
                    self.ema_mean += 0.05 * diff
                    self.ema_var = 0.95 * self.ema_var + 0.05 * (diff ** 2)
                    self.block_scores.clear()
                    self.frame_counter = 0

        return is_alert, lambda_k, self.alpha_k, is_quarantined, self.alert_density_global, float(self.alert_density_id[dense_id])
