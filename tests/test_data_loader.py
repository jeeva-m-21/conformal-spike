"""
Unit tests for Module: data_loader.
Verifies continuous physical CAN timeline across regimes and ROAD masquerade substrate authenticity.
"""

import unittest
from src.data_loader import load_expanded_datasets, CANFrame


class TestDataLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_expanded_datasets()

    def test_regime_timestamps_strictly_monotonic(self):
        """
        Test that regime timestamps are strictly monotonically increasing (t_k > t_{k-1})
        across all frames in every driving regime.
        """
        regimes = self.data["regimes"]
        for regime_name, stream in regimes.items():
            self.assertGreater(len(stream), 0, f"Regime {regime_name} has 0 frames!")
            for i in range(1, len(stream)):
                t_prev = stream[i - 1].timestamp_s
                t_curr = stream[i].timestamp_s
                self.assertGreater(
                    t_curr, t_prev,
                    f"Timestamp non-monotonic in regime {regime_name} at index {i}: {t_curr} <= {t_prev}"
                )

    def test_road_masquerade_synthesized_from_road_substrate(self):
        """
        Test that ROAD masquerade streams (e.g. road_masq_speed) are synthesized
        from authentic DATA_ROAD_PATH frames where CAN ID 0x6E0 is native and periodic,
        rather than Hyundai Sonata cal_benign where 0x6E0 is completely absent.
        """
        road_speed = self.data["road_masq_speed"]
        self.assertGreater(len(road_speed), 0)

        # Check native presence of 0x6E0 in normal/baseline frames
        normal_6e0_count = sum(1 for f in road_speed if f.label == 'Normal' and f.can_id == 0x6E0)
        self.assertGreater(
            normal_6e0_count, 50,
            f"0x6E0 native frames missing from road_masq_speed normal baseline! Found {normal_6e0_count}. "
            f"Masquerade must be synthesized on ORNL ROAD substrate where 0x6E0 is native."
        )

        # Verify attacks exist and are labeled correctly
        attack_count = sum(1 for f in road_speed if f.label != 'Normal')
        self.assertGreater(attack_count, 0, "No attack frames found in road_masq_speed!")


if __name__ == '__main__':
    unittest.main()
