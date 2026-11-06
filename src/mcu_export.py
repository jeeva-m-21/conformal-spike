"""
MCU C Weights & Test Vector Header Exporter for Bare-Metal Firmware Verification.
"""

from typing import List
import numpy as np

from .config import (
    CS_INPUT_DIM,
    CS_HIDDEN_DIM,
    CS_PRED_DIM,
    CS_FENWICK_BINS,
    CS_WINDOW_W,
    CS_MAX_IDS,
)
from .data_loader import CANFrame
from .encoder import PerIDNeuromorphicEncoder
from .models import IDConditionedKWtaSNN


def export_c_headers(
    model: IDConditionedKWtaSNN,
    encoder: PerIDNeuromorphicEncoder,
    cal_scores: np.ndarray,
    test_frames: List[CANFrame],
    weights_path: str = "firmware/conformal_spike_weights.h",
    vectors_path: str = "firmware/test_vectors.h"
):
    print("\n[MCU Export] Exporting Q8.8 fixed-point weights and test vectors to C headers...", flush=True)

    w_in_q8 = (model.fc_in.weight.detach().cpu().numpy() * 127.0).astype(np.int8)
    w_rec_q8 = (model.fc_rec.weight.detach().cpu().numpy() * 127.0).astype(np.int8)
    w_pred_rec_q8 = (model.fc_pred_rec.weight.detach().cpu().numpy() * 127.0).astype(np.int8)
    w_pred_id_q8 = (model.fc_pred_id.weight.detach().cpu().numpy() * 127.0).astype(np.int8)
    beta_q8 = (model.get_beta().detach().cpu().numpy() * 256.0).astype(np.uint8)

    init_bins = [min(CS_FENWICK_BINS, max(1, int(round((s / 3.0) * (CS_FENWICK_BINS - 1))) + 1)) for s in cal_scores[:CS_WINDOW_W]]
    if len(init_bins) < CS_WINDOW_W:
        init_bins.extend([200] * (CS_WINDOW_W - len(init_bins)))

    with open(weights_path, "w") as f:
        f.write("/**\n * Auto-generated fixed-point weights for ConformalSpike MCU Firmware\n */\n")
        f.write("#ifndef CONFORMAL_SPIKE_WEIGHTS_H\n#define CONFORMAL_SPIKE_WEIGHTS_H\n\n#include <stdint.h>\n#include \"conformal_spike_mcu.h\"\n\n")

        # w_in [43][64]
        f.write("static const int8_t g_w_in[CS_INPUT_DIM][CS_HIDDEN_DIM] = {\n")
        for in_ch in range(CS_INPUT_DIM):
            row_str = ", ".join(str(int(w_in_q8[h, in_ch])) for h in range(CS_HIDDEN_DIM))
            f.write(f"    {{{row_str}}},\n")
        f.write("};\n\n")

        # w_rec [64][64]
        f.write("static const int8_t g_w_rec[CS_HIDDEN_DIM][CS_HIDDEN_DIM] = {\n")
        for rec_ch in range(CS_HIDDEN_DIM):
            row_str = ", ".join(str(int(w_rec_q8[h, rec_ch])) for h in range(CS_HIDDEN_DIM))
            f.write(f"    {{{row_str}}},\n")
        f.write("};\n\n")

        # w_pred_rec [64][32]
        f.write("static const int8_t g_w_pred_rec[CS_HIDDEN_DIM][CS_PRED_DIM] = {\n")
        for rec_ch in range(CS_HIDDEN_DIM):
            row_str = ", ".join(str(int(w_pred_rec_q8[p, rec_ch])) for p in range(CS_PRED_DIM))
            f.write(f"    {{{row_str}}},\n")
        f.write("};\n\n")

        # w_pred_id [11][32]
        f.write("static const int8_t g_w_pred_id[11][CS_PRED_DIM] = {\n")
        for id_b in range(11):
            row_str = ", ".join(str(int(w_pred_id_q8[p, id_b])) for p in range(CS_PRED_DIM))
            f.write(f"    {{{row_str}}},\n")
        f.write("};\n\n")

        # beta_q8 [64]
        b_str = ", ".join(str(int(b)) for b in beta_q8)
        f.write(f"static const uint8_t g_beta_q8[CS_HIDDEN_DIM] = {{{b_str}}};\n\n")

        # can_id_to_dense [2048]
        dense_str = ", ".join(str(int(idx)) for idx in encoder.can_id_to_dense)
        f.write(f"static const uint8_t g_can_id_to_dense[2048] = {{{dense_str}}};\n\n")

        # tau_max [CS_MAX_IDS][8]
        f.write("static const uint8_t g_tau_max[CS_MAX_IDS][8] = {\n")
        for i in range(CS_MAX_IDS):
            row_str = ", ".join(str(int(encoder.tau_max[i, j])) for j in range(8))
            f.write(f"    {{{row_str}}},\n")
        f.write("};\n\n")

        # init_cal_bins [8192]
        f.write("static const uint16_t g_init_cal_bins[CS_WINDOW_W] = {\n")
        for i in range(0, CS_WINDOW_W, 16):
            chunk = ", ".join(str(int(b)) for b in init_bins[i:i + 16])
            f.write(f"    {chunk},\n")
        f.write("};\n\n#endif /* CONFORMAL_SPIKE_WEIGHTS_H */\n")

    # Export 2000 test vectors for test_mcu.c
    with open(vectors_path, "w") as f:
        f.write("/**\n * Test vectors for standalone C verification\n */\n")
        f.write("#ifndef TEST_VECTORS_H\n#define TEST_VECTORS_H\n\n#include <stdint.h>\n\n")
        f.write("typedef struct {\n    uint32_t timestamp_us;\n    uint16_t can_id;\n    uint8_t payload[8];\n    uint8_t is_attack;\n} mcu_test_vector_t;\n\n")
        f.write(f"#define NUM_TEST_VECTORS {min(2000, len(test_frames))}U\n\n")
        f.write("static const mcu_test_vector_t g_test_vectors[NUM_TEST_VECTORS] = {\n")
        for i, f_item in enumerate(test_frames[:2000]):
            ts_us = int(f_item.timestamp_s * 1e6) & 0xFFFFFFFF
            cid = f_item.can_id & 0x7FF
            p_bytes = ", ".join(f"0x{b:02X}" for b in f_item.payload[:8])
            if len(f_item.payload) < 8:
                p_bytes += ", " + ", ".join("0x00" for _ in range(8 - len(f_item.payload)))
            is_atk = 1 if f_item.label != 'Normal' else 0
            f.write(f"    {{{ts_us}U, 0x{cid:03X}U, {{{p_bytes}}}, {is_atk}U}},\n")
        f.write("};\n\n#endif /* TEST_VECTORS_H */\n")

    print(f"[MCU Export] Successfully exported {weights_path} and {vectors_path}", flush=True)
