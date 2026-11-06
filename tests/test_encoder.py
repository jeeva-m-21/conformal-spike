"""
Unit tests for Module 1: PerIDNeuromorphicEncoder.
Verifies modular rollover arithmetic, magnitude calibration ceiling, and shadow rollback.
"""

import unittest
import numpy as np
from src.encoder import PerIDNeuromorphicEncoder, SingleIDContext
from src.data_loader import CANFrame


class TestNeuromorphicEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = PerIDNeuromorphicEncoder()
        self.can_id = 0x6E0
        self.encoder.register_ids([self.can_id])

    def test_modular_distance_byte_rollover(self):
        """
        Test that 16-bit counter rollover (0xFF -> 0x00) computes circular modular distance
        min(|p - lp|, 256 - |p - lp|) = 1 rather than linear distance 255.
        """
        dense_id = self.encoder.get_dense_id(self.can_id)
        self.encoder.tau_max[dense_id, 1] = 15

        # Frame 1: Initial payload with byte 1 at 0xFF
        p1 = bytes([0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        spikes1, _ = self.encoder.encode(0.001, self.can_id, p1)

        # Frame 2: Rollover to 0x00 on byte 1 (16-bit counter increments 0x01FF -> 0x0200)
        p2 = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        spikes2, _ = self.encoder.encode(0.002, self.can_id, p2)

        # Magnitude shock channel for byte 1 is at index 27 + 1 = 28
        mag_shock_byte1 = spikes2[28]
        # With modular distance min(255, 1) = 1 <= 15 (tau_max), magnitude shock MUST NOT fire.
        # If buggy linear distance 255 was used, 255 > 15 would falsely fire mag_shock.
        self.assertEqual(
            mag_shock_byte1, 0.0,
            "Byte rollover (0xFF -> 0x00) should have modular distance 1 and not trigger magnitude shock!"
        )

        # Frame 3: True malicious magnitude jump (+200 modular distance)
        p3 = bytes([0x00, 200, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        spikes3, _ = self.encoder.encode(0.003, self.can_id, p3)
        self.assertEqual(
            spikes3[28], 1.0,
            "True magnitude jump (+200 > tau_max=15) must trigger magnitude shock!"
        )

    def test_tau_max_not_inflated_by_rollover(self):
        """
        Test that calibrating on a benign 16-bit counter stream crossing 256-boundaries
        does not inflate tau_max to >240, but keeps tau_max <= 24.
        """
        dense_id = self.encoder.get_dense_id(self.can_id)
        benign_frames = []

        # Simulate a 16-bit counter incrementing across boundaries in 1000 frames
        # Big-endian: byte 0 is high byte, byte 1 is low byte
        for k in range(1000):
            counter = k & 0xFFFF
            b0 = (counter >> 8) & 0xFF
            b1 = counter & 0xFF
            p = bytes([b0, b1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            benign_frames.append(CANFrame(k * 0.0005, self.can_id, p, 'Normal'))

        self.encoder.calibrate_entropy_and_magnitude(benign_frames)
        tau_val = self.encoder.tau_max[dense_id, 1]

        self.assertLessEqual(
            tau_val, 24,
            f"tau_max[{hex(self.can_id)}, 1] is inflated to {tau_val}; should be <= 24 under modular distance!"
        )

    def test_single_id_checkpoint_and_rollback(self):
        """
        Test that 16-byte single-ID context checkpoints prior to frame processing
        and correctly rolls back upon alert if consecutive_rollbacks < 8.
        """
        dense_id = self.encoder.get_dense_id(self.can_id)

        # 1. Establish benign state
        p0 = bytes([0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80])
        self.encoder.encode(0.010, self.can_id, p0)
        self.encoder.conditional_rollback(is_alert=False, timestamp_s=0.010)

        # 2. Inject anomalous frame
        p_atk = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        self.encoder.encode(0.015, self.can_id, p_atk)

        # State before rollback has p_atk
        st = self.encoder.contexts[dense_id]
        self.assertEqual(bytes(st.last_payload), p_atk)

        # 3. Trigger rollback
        rolled_back = self.encoder.conditional_rollback(is_alert=True, timestamp_s=0.015)
        self.assertTrue(rolled_back, "Rollback should return True for isolated alert (<8)")
        # Last payload should be restored to p0
        self.assertEqual(bytes(st.last_payload), p0, "Payload state was not restored to shadow context!")

        # 4. Sustained alert test: after 8 alerts, break deadlock and commit
        for step in range(2, 9):
            self.encoder.encode(0.015 + step * 0.001, self.can_id, p_atk)
            rolled_back = self.encoder.conditional_rollback(is_alert=True, timestamp_s=0.015 + step * 0.001)

        # At consecutive_rollbacks >= 8, deadlock breaks
        self.assertFalse(rolled_back, "Consecutive rollbacks >= 8 must commit to prevent deadlock!")


if __name__ == '__main__':
    unittest.main()
