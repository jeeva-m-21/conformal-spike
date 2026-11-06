"""
Module 1: Multi-scale Log-Delta & Magnitude Shock Stateful Neuromorphic Event Encoder.
"""

import math
import collections
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import (
    CS_MAX_IDS,
    CS_INPUT_DIM,
    CS_PRED_DIM,
    CS_DELTA_THRESH,
)
from .data_loader import CANFrame


class SingleIDContext:
    __slots__ = ('last_timestamp_s', 'ema_period_s', 'last_payload', 'consecutive_rollbacks', 'valid')
    def __init__(self):
        self.last_timestamp_s = 0.0
        self.ema_period_s = 0.010
        self.last_payload = bytearray([0] * 8)
        self.consecutive_rollbacks = 0
        self.valid = False

    def copy(self) -> 'SingleIDContext':
        c = SingleIDContext()
        c.last_timestamp_s = self.last_timestamp_s
        c.ema_period_s = self.ema_period_s
        c.last_payload = bytearray(self.last_payload)
        c.consecutive_rollbacks = self.consecutive_rollbacks
        c.valid = self.valid
        return c


class PerIDNeuromorphicEncoder:
    """
    Module 1: Per-ID Stateful Neuromorphic Event Encoder
    Upgrades:
      - 11-bit arbitration ID spikes
      - 16-bit payload delta sign spikes (diff >= 4 LSB)
      - 8-bit Magnitude Shock Spikes: S_mag[j] = 1 if |diff_j| > tau_max[ID, j]
      - 8-bit log2 timing spikes
      - Entropy weights w_byte[ID, j] in [0.2, 1.0] (dampens CRC/counters)
      - Single-ID 16-byte lightweight checkpoint (8 cycles)
      - Deadlock-Free Conditional Rollback: rolls back on isolated burst (<8 frames),
        breaks rollback lock under continuous legitimate kinematic shifts
    """
    def __init__(self, delta_thresh: int = CS_DELTA_THRESH):
        self.delta_thresh = delta_thresh
        self.input_dim = CS_INPUT_DIM
        self.pred_dim = CS_PRED_DIM

        # Collision-free dense ID table (up to CS_MAX_IDS unique IDs)
        self.can_id_to_dense = np.full(2048, 255, dtype=np.uint8)
        self.dense_to_can_id: List[int] = []

        # Per-ID state contexts (CS_MAX_IDS entries * 16 bytes = 4,096 bytes SRAM)
        self.contexts: List[SingleIDContext] = [SingleIDContext() for _ in range(CS_MAX_IDS)]

        # Calibrated magnitude thresholds tau_max[ID, 8] and entropy weights w_byte[ID, 8]
        self.tau_max = np.full((CS_MAX_IDS, 8), 16, dtype=np.uint8)
        self.w_byte = np.ones((CS_MAX_IDS, 8), dtype=np.float32)

        # Single-ID 16-byte shadow state
        self.shadow_dense_id = 0
        self.shadow_context: Optional[SingleIDContext] = None

    def register_ids(self, can_ids: List[int]):
        for cid in can_ids:
            cid_masked = cid & 0x7FF
            if self.can_id_to_dense[cid_masked] == 255:
                dense_idx = len(self.dense_to_can_id)
                if dense_idx < CS_MAX_IDS:
                    self.can_id_to_dense[cid_masked] = dense_idx
                    self.dense_to_can_id.append(cid_masked)

    def calibrate_entropy_and_magnitude(self, benign_frames: List[CANFrame]):
        print("[Encoder Calibration] Calibrating magnitude thresholds & entropy weights...", flush=True)
        id_deltas: Dict[int, List[List[int]]] = {idx: [[] for _ in range(8)] for idx in range(len(self.dense_to_can_id))}
        id_hist: Dict[int, List[Dict[int, int]]] = {idx: [collections.defaultdict(int) for _ in range(8)] for idx in range(len(self.dense_to_can_id))}
        last_p: Dict[int, bytes] = {}

        for f in benign_frames:
            dense_idx = self.can_id_to_dense[f.can_id & 0x7FF]
            if dense_idx >= len(self.dense_to_can_id):
                continue
            if dense_idx in last_p:
                lp = last_p[dense_idx]
                for j in range(min(8, len(f.payload), len(lp))):
                    raw_d = abs(int(f.payload[j]) - int(lp[j]))
                    d = min(raw_d, 256 - raw_d)
                    id_deltas[dense_idx][j].append(d)
                    id_hist[dense_idx][j][int(f.payload[j])] += 1
            last_p[dense_idx] = f.payload

        for idx in range(len(self.dense_to_can_id)):
            for j in range(8):
                deltas = id_deltas[idx][j]
                if len(deltas) > 50:
                    tau = int(np.percentile(deltas, 99.5))
                    self.tau_max[idx, j] = max(10, min(240, tau))
                else:
                    self.tau_max[idx, j] = 24

                counts = list(id_hist[idx][j].values())
                total = sum(counts)
                if total > 50:
                    probs = [c / total for c in counts]
                    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
                    self.w_byte[idx, j] = float(np.clip(1.0 - (entropy / 8.0) * 0.75, 0.20, 1.0))
                else:
                    self.w_byte[idx, j] = 1.0

        print(f"[Encoder Calibration] Finished for {len(self.dense_to_can_id)} distinct CAN IDs.", flush=True)

    def reset_state(self):
        for c in self.contexts:
            c.last_timestamp_s = 0.0
            c.ema_period_s = 0.010
            c.last_payload = bytearray([0] * 8)
            c.consecutive_rollbacks = 0
            c.valid = False
        self.shadow_context = None

    def get_dense_id(self, can_id: int) -> int:
        dense_idx = self.can_id_to_dense[can_id & 0x7FF]
        return int(dense_idx) if dense_idx < len(self.dense_to_can_id) else 0

    @staticmethod
    def get_asil_weight(can_id: int) -> float:
        return 1.25 if can_id < 0x200 else 1.0

    def encode(self, timestamp_s: float, can_id: int, payload: bytes) -> Tuple[np.ndarray, np.ndarray]:
        dense_idx = self.get_dense_id(can_id)
        st = self.contexts[dense_idx]

        # 16-byte Single-ID Checkpoint (8 CPU cycles)
        self.shadow_dense_id = dense_idx
        self.shadow_context = st.copy()

        spikes = np.zeros(self.input_dim, dtype=np.float32)

        # 1. 11-bit Arbitration ID Spikes
        for b in range(11):
            if (can_id >> b) & 1:
                spikes[b] = 1.0

        # 2. 16-bit Payload Delta Spikes & 8-bit Magnitude Shock Spikes
        delta_offset = 11
        mag_offset = 27
        p_len = min(8, len(payload))

        if st.valid:
            for j in range(p_len):
                raw_diff = int(payload[j]) - int(st.last_payload[j])
                abs_diff = abs(raw_diff)
                mod_diff = min(abs_diff, 256 - abs_diff)
                diff = (raw_diff + 128) % 256 - 128

                # Delta sign channels
                if diff >= self.delta_thresh:
                    spikes[delta_offset + 2 * j] = 1.0
                    st.last_payload[j] = payload[j]
                elif diff <= -self.delta_thresh:
                    spikes[delta_offset + 2 * j + 1] = 1.0
                    st.last_payload[j] = payload[j]

                # Magnitude Shock channel
                if mod_diff > int(self.tau_max[dense_idx, j]):
                    spikes[mag_offset + j] = 1.0

            # 3. 8-bit Log2 Timing Spikes
            dt = max(1e-6, timestamp_s - st.last_timestamp_s)
            expected_dt = st.ema_period_s
            log_ratio = math.log2(dt / max(1e-6, expected_dt))
            bin_idx = int(np.clip(round(log_ratio + 4.0), 0, 7))
            if abs(log_ratio) > 0.20:
                spikes[35 + bin_idx] = 1.0
            if abs(log_ratio) <= 0.50:
                st.ema_period_s = 0.96875 * expected_dt + 0.03125 * dt
        else:
            for j in range(p_len):
                st.last_payload[j] = payload[j]
            st.ema_period_s = 0.010
            st.valid = True

        st.last_timestamp_s = timestamp_s
        readout_target = spikes[11:43].copy()
        return spikes, readout_target

    def conditional_rollback(self, is_alert: bool, timestamp_s: float, is_quarantined: bool = False, has_shock: bool = False) -> bool:
        """
        Deadlock-Free State Rollback:
          - If has_shock == True:
            Physical actuator magnitude shock detected. ALWAYS revert to shadow context
            without poison commitment; return True (rolled back).
          - If is_quarantined == True:
            ECU/Bus is quarantined. Revert active ID's payload to shadow context up to 8 frames;
            break deadlock under sustained non-shock regime shifts.
          - If is_alert == True (and not quarantined):
            If pre-frame state was valid and consecutive_rollbacks < 8 (isolated anomalous burst):
              Revert active ID's payload to shadow context and return True (rolled back).
            Else:
              Break deadlock! Under sustained legitimate traffic shifts, commit current payload
              so the system adapts to valid kinematic transitions; return False (committed).
          - If is_alert == False:
            Commit benign observation. If consecutive_rollbacks > 5, resynchronize timestamp.
            Reset consecutive_rollbacks = 0; return False (committed).
        """
        st = self.contexts[self.shadow_dense_id]
        if has_shock:
            if self.shadow_context is not None and self.shadow_context.valid:
                st.last_payload = bytearray(self.shadow_context.last_payload)
                return True
            return False
        if is_quarantined:
            st.consecutive_rollbacks += 1
            if self.shadow_context is not None and self.shadow_context.valid and (st.consecutive_rollbacks < 8):
                st.last_payload = bytearray(self.shadow_context.last_payload)
                return True
            else:
                # Break deadlock under sustained legitimate non-stationary regime shift
                st.consecutive_rollbacks = 0
                return False
        if is_alert:
            st.consecutive_rollbacks += 1
            if self.shadow_context is not None and self.shadow_context.valid and (st.consecutive_rollbacks < 8):
                st.last_payload = bytearray(self.shadow_context.last_payload)
                return True
            else:
                # Break deadlock: commit observation
                st.consecutive_rollbacks = 0
                return False
        else:
            if st.consecutive_rollbacks > 5:
                st.last_timestamp_s = timestamp_s
            st.consecutive_rollbacks = 0
            return False
