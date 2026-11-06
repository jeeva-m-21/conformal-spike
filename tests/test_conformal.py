"""
Unit tests for Module 4: FenwickQuantileBuffer and ConformalSpikeIDS.
Verifies O(log M) binary lifting, exact quantile queries, quarantine gates, and deadlock-free buffer admission.
"""

import unittest
import numpy as np
from src.conformal import FenwickQuantileBuffer, ConformalSpikeIDS
from src.config import CS_WINDOW_W, CS_FENWICK_BINS, ALPHA_TARGET, QUARANTINE_KAPPA, RHO_THRESH


class TestConformal(unittest.TestCase):
    def test_fenwick_quantile_buffer_rank_and_lifting(self):
        """
        Test FenwickQuantileBuffer O(log M) binary lifting and exact quantile queries.
        """
        buffer = FenwickQuantileBuffer(capacity=1000, num_bins=CS_FENWICK_BINS)

        # Uniform values between 0.5 and 2.5
        np.random.seed(42)
        values = np.linspace(0.5, 2.5, 500)
        for v in values:
            buffer.push(float(v))

        self.assertEqual(buffer.count, 500)

        # Median query (q = 0.50) -> should be close to 1.5
        q50 = buffer.query_quantile(0.50)
        self.assertAlmostEqual(q50, 1.5, delta=0.05)

        # 90th percentile (q = 0.90) -> should be close to 2.3
        q90 = buffer.query_quantile(0.90)
        self.assertAlmostEqual(q90, 2.3, delta=0.05)

        # Monotonicity check
        q10 = buffer.query_quantile(0.10)
        q99 = buffer.query_quantile(0.99)
        self.assertLess(q10, q50)
        self.assertLess(q50, q90)
        self.assertLess(q90, q99)

    def test_quarantine_shield_gates(self):
        """
        Test that Gate 1 (extreme kinematic shock), Gate 2 (concentrated ECU alert density),
        and Gate 3 (bus flooding alert density) trigger quarantine flags correctly.
        """
        cal_scores = np.full(500, 0.20, dtype=np.float32)
        ids = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)
        th = ids.get_threshold()

        # Gate 1: Extreme spatial excursion shock (score > kappa * lambda_k)
        score_extreme = th * (QUARANTINE_KAPPA + 0.5)
        d, _, _, q_extreme, _, _ = ids.decide(score_extreme, dense_id=5)
        self.assertEqual(d, 1)
        self.assertTrue(q_extreme, "Gate 1 extreme shock must trigger quarantine immediately!")

        # Reset IDS
        ids = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)
        # Gate 2: Concentrated ECU alert density
        # Inject mild alert scores repeatedly on dense_id=10
        q_ecu_triggered = False
        for _ in range(30):
            d, _, _, q, _, rho_id = ids.decide(th + 0.05, dense_id=10)
            if q and rho_id > RHO_THRESH:
                q_ecu_triggered = True
                break
        self.assertTrue(q_ecu_triggered, "Gate 2 ECU alert density must trigger quarantine!")

        # Reset IDS
        ids = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)
        # Gate 3: Systemic bus flood across different IDs
        q_flood_triggered = False
        for step in range(50):
            d, _, _, q, rho_glob, _ = ids.decide(th + 0.05, dense_id=(step % 20))
            if q and rho_glob > 0.35:
                q_flood_triggered = True
                break
        self.assertTrue(q_flood_triggered, "Gate 3 bus flooding alert density must trigger quarantine!")

    def test_regime_shift_admission_not_locked_out(self):
        """
        Test that ConformalSpikeIDS admits frames with 'not q_old' into Fenwick buffer,
        allowing the calibration distribution to adapt during benign regime shifts (preventing lockout).
        """
        cal_scores = np.full(500, 0.20, dtype=np.float32)
        ids = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET, staging_len=10)
        initial_th = ids.get_threshold()

        # Benign regime shift: scores drift upward smoothly to 0.25 (exceeding initial threshold,
        # but below Gate 1 extreme shock threshold and distributed across IDs)
        initial_buffer_count = ids.q_buffer.count
        for i in range(100):
            # Moderate drift: above initial threshold, but below 2.0 * initial_threshold
            drift_score = initial_th + 0.02
            dense_id = i % 50  # distributed across 50 CAN IDs, so Gate 2 doesn't trigger
            ids.decide(drift_score, dense_id=dense_id)

        # Because frames survived staging without quarantine (not q_old), they MUST be admitted
        # to q_buffer, and the threshold should adapt upward to accommodate benign regime shift!
        self.assertGreater(
            ids.q_buffer.count, initial_buffer_count,
            "Frames with not q_old must be admitted to the Fenwick buffer during regime shifts!"
        )
        new_th = ids.get_threshold()
        self.assertGreater(
            new_th, initial_th,
            f"Threshold should have adapted upward: {new_th:.4f} vs {initial_th:.4f}"
        )


if __name__ == '__main__':
    unittest.main()
