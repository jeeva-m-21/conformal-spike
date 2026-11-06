"""
Unit tests for Module 2: IDConditionedKWtaSNN.
Verifies k-WTA lateral inhibition (strictly K=12 spikes), soft resets, and voltage clamping.
"""

import unittest
import torch
from src.models import IDConditionedKWtaSNN
from src.config import CS_INPUT_DIM, CS_HIDDEN_DIM, CS_PRED_DIM, CS_K_WTA, CS_V_TH, CS_V_CEIL


class TestModels(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(42)
        self.snn = IDConditionedKWtaSNN(
            input_dim=CS_INPUT_DIM,
            hidden_dim=CS_HIDDEN_DIM,
            pred_dim=CS_PRED_DIM,
            k_wta=CS_K_WTA,
            v_th=CS_V_TH,
            v_ceil=CS_V_CEIL
        )

    def test_k_wta_lateral_inhibition_strictly_k_spikes(self):
        """
        Test that when all 64 hidden neurons receive strong excitation exceeding v_th,
        k-WTA lateral inhibition selects strictly K=12 winning neurons.
        """
        # Create strong input so all 64 neurons receive large synaptic current
        s_in = torch.ones(1, CS_INPUT_DIM)
        # Large initial membrane potential
        v_prev = torch.full((1, CS_HIDDEN_DIM), 2.0)
        s_prev = torch.zeros(1, CS_HIDDEN_DIM)

        pred_probs, v_next, s_hid, mes_score, exact_acs = self.snn.forward_step(s_in, v_prev, s_prev)

        total_spikes = int(s_hid.sum().item())
        self.assertEqual(
            total_spikes, CS_K_WTA,
            f"k-WTA lateral inhibition must select strictly K={CS_K_WTA} spikes, but got {total_spikes}!"
        )

    def test_soft_reset_and_voltage_clamping(self):
        """
        Test that winning firing neurons undergo soft-reset (v_next = v_pre - v_th)
        while suppressed non-firing neurons are clamped at v_ceil.
        """
        s_in = torch.ones(1, CS_INPUT_DIM)
        v_prev = torch.full((1, CS_HIDDEN_DIM), 3.0)
        s_prev = torch.zeros(1, CS_HIDDEN_DIM)

        _, v_next, s_hid, _, _ = self.snn.forward_step(s_in, v_prev, s_prev)

        # Re-derive v_pre to test exact math
        beta = self.snn.get_beta()
        i_syn = self.snn.fc_in(s_in) + self.snn.fc_rec(s_prev)
        v_pre = beta * v_prev + i_syn

        for i in range(CS_HIDDEN_DIM):
            if s_hid[0, i] > 0.0:
                # Firing neuron: soft reset
                expected_v = (v_pre[0, i] - CS_V_TH).item()
                actual_v = v_next[0, i].item()
                self.assertAlmostEqual(actual_v, expected_v, places=4,
                                       msg=f"Neuron {i} fired but did not soft-reset properly!")
            else:
                # Suppressed neuron: clamped to <= v_ceil
                actual_v = v_next[0, i].item()
                self.assertLessEqual(actual_v, CS_V_CEIL + 1e-4,
                                     msg=f"Neuron {i} was suppressed but exceeded v_ceil!")


if __name__ == '__main__':
    unittest.main()
