"""
Statistical Evaluation, Confidence Intervals, and Benchmark Protocols:
  - compute_bootstrap_ci
  - run_table_i_regime_shifts
  - run_table_ii_attacks
  - run_adversarial_pulse_sweep
  - run_ablation_study
  - run_pulse_attack_simulation
"""

import collections
from typing import Dict, List, Tuple, Any
import numpy as np
import torch

from .config import ALPHA_TARGET, CS_HIDDEN_DIM
from .data_loader import CANFrame
from .encoder import PerIDNeuromorphicEncoder
from .models import IDConditionedKWtaSNN, compute_frame_score
from .conformal import ConformalSpikeIDS
from .baselines import (
    INT8TinyMLPAutoencoder,
    INT8MicroGRU,
    StatisticalTimingEntropyIDS,
    HeuristicStaticIDS,
    SplitConformalIDS,
    UnguardedOnlineACIIDS,
    AlertGatedOnlineACIIDS,
    NonNeuralDeltaConformalIDS,
)


def compute_bootstrap_ci(
    data: List[float],
    n_boot: int = 10000,
    alpha: float = 0.05,
    seed: int = 42
) -> Tuple[float, float, float, float]:
    """
    Computes empirical mean, sample standard deviation, and 95% bootstrap confidence interval.
    """
    arr = np.array(data, dtype=np.float64)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    if len(arr) <= 1 or std_val < 1e-9:
        return mean_val, std_val, mean_val, mean_val
    rng = np.random.RandomState(seed)
    boot_means = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    ci_low = float(np.percentile(boot_means, 100.0 * (alpha / 2.0)))
    ci_high = float(np.percentile(boot_means, 100.0 * (1.0 - alpha / 2.0)))
    return mean_val, std_val, ci_low, ci_high


def run_table_i_regime_shifts(
    model: IDConditionedKWtaSNN,
    encoder: PerIDNeuromorphicEncoder,
    regimes: Dict[str, List[CANFrame]],
    cal_scores: np.ndarray,
    cal_benign: List[CANFrame]
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, List[int]]]:
    print("\n============================================================================", flush=True)
    print("TABLE I BENCHMARK: NON-STATIONARY DRIVING REGIME SHIFTS", flush=True)
    print("============================================================================", flush=True)

    m1_static = HeuristicStaticIDS(cal_scores)
    m2_split = SplitConformalIDS(cal_scores, alpha_target=ALPHA_TARGET)
    m3_aci = UnguardedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)
    m4_gated = AlertGatedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)

    # Authentic calibration of non-neural baseline on benign calibration frames
    temp_nn = NonNeuralDeltaConformalIDS(np.array([0.1], dtype=np.float32), alpha_target=ALPHA_TARGET)
    nn_cal = []
    for bf in cal_benign:
        sc_nn = temp_nn.compute_score(bf.can_id, bf.payload)
        temp_nn.last_payload[bf.can_id] = bf.payload
        nn_cal.append(sc_nn)
    m5_nonneural = NonNeuralDeltaConformalIDS(np.array(nn_cal, dtype=np.float32), alpha_target=ALPHA_TARGET)
    m6_conformal = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)

    results = {
        "Heuristic Static (mu + 3*sigma)": {"Stationary": 0, "Highway": 0, "Dyno": 0, "CrossVehicle": 0},
        "Split Conformal (Massaad et al.)": {"Stationary": 0, "Highway": 0, "Dyno": 0, "CrossVehicle": 0},
        "Unguarded Online ACI (Gibbs & Candes)": {"Stationary": 0, "Highway": 0, "Dyno": 0, "CrossVehicle": 0},
        "Alert-Gated Online ACI (Skip on Alert)": {"Stationary": 0, "Highway": 0, "Dyno": 0, "CrossVehicle": 0},
        "Non-Neural Delta + Conformal": {"Stationary": 0, "Highway": 0, "Dyno": 0, "CrossVehicle": 0},
        "ConformalSpike (Proposed G-RW-CRC)": {"Stationary": 0, "Highway": 0, "Dyno": 0, "CrossVehicle": 0},
    }

    history = {k: [] for k in results.keys()}
    encoder.reset_state()
    v_base = torch.zeros(1, CS_HIDDEN_DIM)
    s_base = torch.zeros(1, CS_HIDDEN_DIM)
    v_cs = torch.zeros(1, CS_HIDDEN_DIM)
    s_cs = torch.zeros(1, CS_HIDDEN_DIM)

    # 1. Warm-up pass on authentic stationary frames
    for f in regimes["Warmup"]:
        s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)
        dense_id = encoder.get_dense_id(f.can_id)
        sc_b, v_base, s_base, _ = compute_frame_score(model, s_in, v_base, s_base, dense_id, encoder)
        m1_static.decide(sc_b)
        m2_split.decide(sc_b)
        m3_aci.decide(sc_b)
        m4_gated.decide(sc_b)
        m5_nonneural.decide(f.can_id, f.payload)

        sc_cs, v_n_cs, s_n_cs, _ = compute_frame_score(model, s_in, v_cs, s_cs, dense_id, encoder)
        d_cs, _, _, q_cs, _, _ = m6_conformal.decide(sc_cs, dense_id)
        rolled_back = encoder.conditional_rollback(is_alert=(d_cs == 1), timestamp_s=f.timestamp_s, is_quarantined=q_cs)
        if not rolled_back:
            v_cs, s_cs = v_n_cs, s_n_cs

    # 2. Sequential 4-Regime Driving Streams (10,000 frames each, 40,000 total)
    test_regimes = ["Stationary", "Highway", "Dyno", "CrossVehicle"]
    commissioning_counts: Dict[int, int] = collections.defaultdict(int)
    commissioning_jumps: Dict[int, List[int]] = collections.defaultdict(lambda: [0] * 8)

    for reg_name in test_regimes:
        f_list = regimes[reg_name]
        print(f"  Streaming authentic regime: {reg_name:12s} ({len(f_list):,} frames)...", flush=True)

        for f in f_list:
            dense_id = encoder.get_dense_id(f.can_id)
            is_comm = False
            if reg_name == "CrossVehicle":
                c_cnt = commissioning_counts[dense_id]
                if c_cnt < 5:
                    is_comm = True
                    commissioning_counts[dense_id] += 1
                    st = encoder.contexts[dense_id]
                    if st.valid:
                        for j in range(min(8, len(f.payload), len(st.last_payload))):
                            raw_d = abs(int(f.payload[j]) - int(st.last_payload[j]))
                            mod_d = min(raw_d, 256 - raw_d)
                            if mod_d > 15:
                                commissioning_jumps[dense_id][j] += 1
                                if commissioning_jumps[dense_id][j] >= 2:
                                    encoder.tau_max[dense_id, j] = 128

            s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)

            sc_b, v_base, s_base, _ = compute_frame_score(model, s_in, v_base, s_base, dense_id, encoder)
            d1 = m1_static.decide(sc_b)
            d2 = m2_split.decide(sc_b)
            d3, _, _ = m3_aci.decide(sc_b)
            d4, _, _ = m4_gated.decide(sc_b)
            d5, _, _ = m5_nonneural.decide(f.can_id, f.payload)

            results["Heuristic Static (mu + 3*sigma)"][reg_name] += d1
            results["Split Conformal (Massaad et al.)"][reg_name] += d2
            results["Unguarded Online ACI (Gibbs & Candes)"][reg_name] += d3
            results["Alert-Gated Online ACI (Skip on Alert)"][reg_name] += d4
            results["Non-Neural Delta + Conformal"][reg_name] += d5

            history["Heuristic Static (mu + 3*sigma)"].append(d1)
            history["Split Conformal (Massaad et al.)"].append(d2)
            history["Unguarded Online ACI (Gibbs & Candes)"].append(d3)
            history["Alert-Gated Online ACI (Skip on Alert)"].append(d4)
            history["Non-Neural Delta + Conformal"].append(d5)

            # Proposed ConformalSpike with Deadlock-Free Rollback
            sc_cs, v_n_cs, s_n_cs, _ = compute_frame_score(model, s_in, v_cs, s_cs, dense_id, encoder)
            d6, _, _, q6, _, _ = m6_conformal.decide(sc_cs, dense_id)
            if is_comm:
                q6 = True
            rolled_back = encoder.conditional_rollback(is_alert=(d6 == 1), timestamp_s=f.timestamp_s, is_quarantined=q6)
            if not rolled_back:
                v_cs, s_cs = v_n_cs, s_n_cs

            results["ConformalSpike (Proposed G-RW-CRC)"][reg_name] += d6
            history["ConformalSpike (Proposed G-RW-CRC)"].append(d6)

    table_data = {}
    for k in results.keys():
        fpr_stat = (results[k]["Stationary"] / 10000.0) * 100.0
        fpr_hwy  = (results[k]["Highway"] / 10000.0) * 100.0
        fpr_dyno = (results[k]["Dyno"] / 10000.0) * 100.0
        fpr_xv   = (results[k]["CrossVehicle"] / 10000.0) * 100.0
        mean_fpr = (fpr_stat + fpr_hwy + fpr_dyno + fpr_xv) / 4.0
        cov_dev  = abs(mean_fpr - (ALPHA_TARGET * 100.0))
        table_data[k] = {
            "Stationary": fpr_stat,
            "Highway": fpr_hwy,
            "Dyno": fpr_dyno,
            "CrossVehicle": fpr_xv,
            "MeanFPR": mean_fpr,
            "Deviation": cov_dev
        }
        print(f"  {k:38s} | Stat: {fpr_stat:5.2f}% | Hwy: {fpr_hwy:5.2f}% | Dyno: {fpr_dyno:5.2f}% | XV: {fpr_xv:5.2f}% | Mean: {mean_fpr:5.2f}%", flush=True)

    return table_data, history


def run_table_ii_attacks(
    model: IDConditionedKWtaSNN,
    mlp: INT8TinyMLPAutoencoder,
    gru: INT8MicroGRU,
    encoder: PerIDNeuromorphicEncoder,
    attack_suites: Dict[str, List[CANFrame]],
    cal_scores: np.ndarray,
    cal_benign: List[CANFrame]
) -> Dict[str, Dict[str, float]]:
    print("\n============================================================================", flush=True)
    print("TABLE II BENCHMARK: ATTACK DETECTION TPR ACROSS ATTACK CLASSES", flush=True)
    print("============================================================================", flush=True)

    tpr_results: Dict[str, Dict[str, float]] = {
        "Split Conformal + Memoryless SNN": {},
        "Stateful SNN + Unguarded ACI": {},
        "Stateful SNN + Alert-Gated ACI": {},
        "Statistical/Timing-Entropy IDS": {},
        "Non-Neural Delta + Conformal": {},
        "INT8 Tiny-MLP Autoencoder": {},
        "INT8 Micro-GRU": {},
        "ConformalSpike (Proposed G-RW-CRC)": {},
    }

    stat_ids = StatisticalTimingEntropyIDS()

    # Pre-calibrate all baselines on their own model predictions over cal_benign
    encoder.reset_state()
    nn_cal = []
    temp_nn = NonNeuralDeltaConformalIDS(np.array([0.1], dtype=np.float32), alpha_target=ALPHA_TARGET)
    mlp_cal = []
    gru_cal = []
    h_cal = torch.zeros(1, 1, 64)
    for bf in cal_benign:
        sc_nn = temp_nn.compute_score(bf.can_id, bf.payload)
        temp_nn.last_payload[bf.can_id] = bf.payload
        nn_cal.append(sc_nn)

        s_in, tgt = encoder.encode(bf.timestamp_s, bf.can_id, bf.payload)
        with torch.no_grad():
            p_m = mlp(torch.from_numpy(s_in).unsqueeze(0).float()).squeeze(0).numpy()
            p_g, h_cal = gru(torch.from_numpy(s_in).unsqueeze(0).unsqueeze(0).float(), h_cal)
        mlp_cal.append(float(np.mean(np.abs(tgt - p_m))) * 3.0)
        gru_cal.append(float(np.mean(np.abs(tgt - p_g.squeeze().numpy()))) * 3.0)

    nn_cal_arr = np.array(nn_cal, dtype=np.float32)
    mlp_cal_arr = np.array(mlp_cal, dtype=np.float32)
    gru_cal_arr = np.array(gru_cal, dtype=np.float32)

    for atk_name, test_stream in attack_suites.items():
        total_frames = len(test_stream)
        total_atk = sum(1 for f in test_stream if f.label != 'Normal')
        if total_atk == 0:
            total_atk = total_frames

        print(f"  Evaluating Attack Suite: {atk_name:38s} ({total_frames:,} frames, {total_atk:,} attack frames)...", flush=True)

        # 1. Proposed ConformalSpike
        cs_det = 0
        cs_ids = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)
        encoder.reset_state()
        v_h = torch.zeros(1, CS_HIDDEN_DIM)
        s_h = torch.zeros(1, CS_HIDDEN_DIM)

        for f in test_stream:
            is_atk = (f.label != 'Normal')
            s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            dense_id = encoder.get_dense_id(f.can_id)
            sc, v_n, s_n, _ = compute_frame_score(model, s_in, v_h, s_h, dense_id, encoder)
            has_shock = bool(np.sum(tgt[16:24]) >= 1 or tgt[24] >= 1.0)
            d, _, _, q, _, _ = cs_ids.decide(sc, dense_id, has_shock=has_shock)
            if (d == 1 or q) and is_atk:
                cs_det += 1
            rolled_back = encoder.conditional_rollback(d == 1, f.timestamp_s, is_quarantined=q, has_shock=has_shock)
            if not rolled_back:
                v_h, s_h = v_n, s_n
        tpr_results["ConformalSpike (Proposed G-RW-CRC)"][atk_name] = (cs_det / total_atk) * 100.0

        # 2. Stateful SNN + Unguarded ACI
        aci_det = 0
        aci_ids = UnguardedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)
        encoder.reset_state()
        v_h = torch.zeros(1, CS_HIDDEN_DIM)
        s_h = torch.zeros(1, CS_HIDDEN_DIM)

        for f in test_stream:
            is_atk = (f.label != 'Normal')
            s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            dense_id = encoder.get_dense_id(f.can_id)
            sc, v_n, s_n, _ = compute_frame_score(model, s_in, v_h, s_h, dense_id, encoder)
            d, _, _ = aci_ids.decide(sc)
            if d == 1 and is_atk:
                aci_det += 1
            v_h, s_h = v_n, s_n
        tpr_results["Stateful SNN + Unguarded ACI"][atk_name] = (aci_det / total_atk) * 100.0

        # 3. Stateful SNN + Alert-Gated ACI
        gated_det = 0
        gated_ids = AlertGatedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)
        encoder.reset_state()
        v_h = torch.zeros(1, CS_HIDDEN_DIM)
        s_h = torch.zeros(1, CS_HIDDEN_DIM)

        for f in test_stream:
            is_atk = (f.label != 'Normal')
            s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            dense_id = encoder.get_dense_id(f.can_id)
            sc, v_n, s_n, _ = compute_frame_score(model, s_in, v_h, s_h, dense_id, encoder)
            d, _, _ = gated_ids.decide(sc)
            if d == 1 and is_atk:
                gated_det += 1
            if d == 0:
                v_h, s_h = v_n, s_n
        tpr_results["Stateful SNN + Alert-Gated ACI"][atk_name] = (gated_det / total_atk) * 100.0

        # 4. Split Conformal + Memoryless SNN
        memless_det = 0
        split_ids = SplitConformalIDS(cal_scores, alpha_target=ALPHA_TARGET)
        encoder.reset_state()

        for f in test_stream:
            is_atk = (f.label != 'Normal')
            s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            dense_id = encoder.get_dense_id(f.can_id)
            sc, _, _, _ = compute_frame_score(model, s_in, torch.zeros(1, CS_HIDDEN_DIM), torch.zeros(1, CS_HIDDEN_DIM), dense_id, encoder)
            if split_ids.decide(sc) == 1 and is_atk:
                memless_det += 1
        tpr_results["Split Conformal + Memoryless SNN"][atk_name] = (memless_det / total_atk) * 100.0

        # 5. Non-Neural Delta + Conformal
        nonneural_det = 0
        nonneural_ids = NonNeuralDeltaConformalIDS(nn_cal_arr, alpha_target=ALPHA_TARGET)
        for f in test_stream:
            is_atk = (f.label != 'Normal')
            d_nn, _, _ = nonneural_ids.decide(f.can_id, f.payload)
            if d_nn == 1 and is_atk:
                nonneural_det += 1
        tpr_results["Non-Neural Delta + Conformal"][atk_name] = (nonneural_det / total_atk) * 100.0

        # 6. Statistical/Timing-Entropy IDS
        stat_det = 0
        for f in test_stream:
            is_atk = (f.label != 'Normal')
            d_st, _ = stat_ids.decide(f.timestamp_s, f.can_id, f.payload)
            if d_st == 1 and is_atk:
                stat_det += 1
        tpr_results["Statistical/Timing-Entropy IDS"][atk_name] = (stat_det / total_atk) * 100.0

        # 7. INT8 Tiny-MLP Autoencoder
        mlp_det = 0
        mlp_ids = SplitConformalIDS(mlp_cal_arr, alpha_target=ALPHA_TARGET)
        encoder.reset_state()
        for f in test_stream:
            is_atk = (f.label != 'Normal')
            s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            with torch.no_grad():
                p_mlp = mlp(torch.from_numpy(s_in).unsqueeze(0).float()).squeeze(0).numpy()
            sc_mlp = float(np.mean(np.abs(tgt - p_mlp))) * 3.0
            if mlp_ids.decide(sc_mlp) == 1 and is_atk:
                mlp_det += 1
        tpr_results["INT8 Tiny-MLP Autoencoder"][atk_name] = (mlp_det / total_atk) * 100.0

        # 8. INT8 Micro-GRU
        gru_det = 0
        gru_ids = SplitConformalIDS(gru_cal_arr, alpha_target=ALPHA_TARGET)
        encoder.reset_state()
        h_gru = torch.zeros(1, 1, 64)
        for f in test_stream:
            is_atk = (f.label != 'Normal')
            s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            with torch.no_grad():
                p_gru, h_gru = gru(torch.from_numpy(s_in).unsqueeze(0).unsqueeze(0).float(), h_gru)
            sc_gru = float(np.mean(np.abs(tgt - p_gru.squeeze().numpy()))) * 3.0
            if gru_ids.decide(sc_gru) == 1 and is_atk:
                gru_det += 1
        tpr_results["INT8 Micro-GRU"][atk_name] = (gru_det / total_atk) * 100.0

        print(f"    -> ConformalSpike TPR: {tpr_results['ConformalSpike (Proposed G-RW-CRC)'][atk_name]:.2f}% | Unguarded ACI TPR: {tpr_results['Stateful SNN + Unguarded ACI'][atk_name]:.2f}% | Stat IDS TPR: {tpr_results['Statistical/Timing-Entropy IDS'][atk_name]:.2f}%", flush=True)

    return tpr_results


def run_adversarial_pulse_sweep(
    model: IDConditionedKWtaSNN,
    encoder: PerIDNeuromorphicEncoder,
    benign_frames: List[CANFrame],
    cal_scores: np.ndarray
) -> Dict[str, Dict[str, float]]:
    print("\n============================================================================", flush=True)
    print("BENCHMARK: ADVERSARIAL ADAPTIVE ATTACK DUTY CYCLE SWEEP (f_atk in [0.01, 1.0])", flush=True)
    print("============================================================================", flush=True)

    pulse_ratios = [
        ("1-on-100-off (1.0%)", 1, 100),
        ("1-on-50-off (2.0%)",  1, 50),
        ("1-on-20-off (4.8%)",  1, 20),
        ("1-on-10-off (9.1%)",  1, 10),
        ("1-on-4-off (20.0%)",  1, 4),
        ("1-on-2-off (33.3%)",  1, 2),
        ("1-on-1-off (50.0%)",  1, 1),
        ("2-on-1-off (66.7%)",  2, 1),
        ("Continuous (100.0%)", 1, 0),
    ]

    sweep_results: Dict[str, Dict[str, float]] = {
        "Heuristic Static (mu + 3*sigma)": {},
        "Split Conformal (Massaad et al.)": {},
        "Unguarded Online ACI (Gibbs & Candes)": {},
        "Alert-Gated Online ACI (Skip on Alert)": {},
        "ConformalSpike (Proposed G-RW-CRC)": {},
    }

    num_test_frames = 2000

    for name, a_on, b_off in pulse_ratios:
        period = a_on + b_off if b_off > 0 else 1
        duty = a_on / period

        m1 = HeuristicStaticIDS(cal_scores)
        m2 = SplitConformalIDS(cal_scores, alpha_target=ALPHA_TARGET)
        m3 = UnguardedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)
        m4 = AlertGatedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)
        m5 = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)

        encoder.reset_state()
        v_h1 = torch.zeros(1, CS_HIDDEN_DIM)
        s_h1 = torch.zeros(1, CS_HIDDEN_DIM)
        v_h5 = torch.zeros(1, CS_HIDDEN_DIM)
        s_h5 = torch.zeros(1, CS_HIDDEN_DIM)

        d1_atk, d2_atk, d3_atk, d4_atk, d5_atk = 0, 0, 0, 0, 0
        total_atk = 0

        t_curr = 0.0
        for k in range(num_test_frames):
            t_curr += 0.0005
            is_atk = False
            if 200 <= k < 1800:
                pos = (k - 200) % period
                if pos < a_on:
                    is_atk = True
                    total_atk += 1

            bf = benign_frames[k % len(benign_frames)]
            cid = 0x6E0 if is_atk else bf.can_id
            p = bytearray(bf.payload.ljust(8, b'\x00'))
            if is_atk:
                p[1] = 0xFF  # Max Speedometer Masquerade ceiling (255 km/h)

            s_in, tgt = encoder.encode(t_curr, cid, bytes(p))
            dense_id = encoder.get_dense_id(cid)

            # Baselines
            sc1, v_h1, s_h1, _ = compute_frame_score(model, s_in, v_h1, s_h1, dense_id, encoder)
            if m1.decide(sc1) == 1 and is_atk:
                d1_atk += 1
            if m2.decide(sc1) == 1 and is_atk:
                d2_atk += 1
            d3_val, _, _ = m3.decide(sc1)
            if d3_val == 1 and is_atk:
                d3_atk += 1
            d4_val, _, _ = m4.decide(sc1)
            if d4_val == 1 and is_atk:
                d4_atk += 1

            # Proposed ConformalSpike
            has_shock = bool(np.sum(tgt[16:24]) >= 1)
            sc5, v_n5, s_n5, _ = compute_frame_score(model, s_in, v_h5, s_h5, dense_id, encoder)
            d5_val, _, _, q5, _, _ = m5.decide(sc5, dense_id, has_shock=has_shock)
            if (d5_val == 1 or q5) and is_atk:
                d5_atk += 1

            rolled_back = encoder.conditional_rollback(d5_val == 1, t_curr, is_quarantined=q5, has_shock=has_shock)
            if not rolled_back:
                v_h5, s_h5 = v_n5, s_n5

        tpr1 = (d1_atk / max(1, total_atk)) * 100.0
        tpr2 = (d2_atk / max(1, total_atk)) * 100.0
        tpr3 = (d3_atk / max(1, total_atk)) * 100.0
        tpr4 = (d4_atk / max(1, total_atk)) * 100.0
        tpr5 = (d5_atk / max(1, total_atk)) * 100.0

        sweep_results["Heuristic Static (mu + 3*sigma)"][name] = tpr1
        sweep_results["Split Conformal (Massaad et al.)"][name] = tpr2
        sweep_results["Unguarded Online ACI (Gibbs & Candes)"][name] = tpr3
        sweep_results["Alert-Gated Online ACI (Skip on Alert)"][name] = tpr4
        sweep_results["ConformalSpike (Proposed G-RW-CRC)"][name] = tpr5

        print(f"  Pulse: {name:22s} (Duty {duty*100.0:4.1f}%) | ConformalSpike TPR: {tpr5:5.2f}% | AlertGated TPR: {tpr4:5.2f}% | Unguarded ACI TPR: {tpr3:5.2f}%", flush=True)

    return sweep_results


def run_ablation_study(
    model: IDConditionedKWtaSNN,
    encoder: PerIDNeuromorphicEncoder,
    regimes: Dict[str, List[CANFrame]],
    attack_suites: Dict[str, List[CANFrame]],
    cal_frames: List[CANFrame]
) -> List[Dict[str, Any]]:
    print("\n============================================================================", flush=True)
    print("TABLE V BENCHMARK: 6-ROW SYSTEMATIC ABLATION STUDY", flush=True)
    print("============================================================================", flush=True)

    # 6 Ablation Configurations:
    # 1. Full Proposed ConformalSpike
    # 2. w/o ID-Conditioning (fc_pred_id zeroed out)
    # 3. w/o Magnitude Shock (Sign-Only 1-LSB)
    # 4. w/o k-WTA Lateral Inhibition (K_max = 64)
    # 5. w/o Quarantine Shield & Staging (Standard RW-ACI)
    # 6. w/o Rollback (Continuous State Commits)
    configs = [
        ("Full Proposed ConformalSpike", False, False, 12, False, False),
        ("w/o ID-Conditioning (Unconditional)", True, False, 12, False, False),
        ("w/o Magnitude Shock (Sign-Only 1-LSB)", False, True, 12, False, False),
        ("w/o k-WTA Inhibition (Uncapped K=64)", False, False, 64, False, False),
        ("w/o Quarantine Shield & Staging", False, False, 12, True, False),
        ("w/o Atomic Shadow Rollback", False, False, 12, False, True),
    ]

    ablation_rows = []

    for name, zero_id, zero_mag, k_val, disable_quarantine, disable_rollback in configs:
        ab_model = IDConditionedKWtaSNN(k_wta=k_val)
        ab_model.load_state_dict(model.state_dict())
        if zero_id:
            ab_model.fc_pred_id.weight.data.zero_()

        # Step 1: Calibrate this ablation variant with its OWN model scores!
        encoder.reset_state()
        v_h_cal = torch.zeros(1, CS_HIDDEN_DIM)
        s_h_cal = torch.zeros(1, CS_HIDDEN_DIM)
        ab_cal_scores = []
        for f in cal_frames:
            s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            if zero_mag:
                s_in[27:35] = 0.0
            dense_id = encoder.get_dense_id(f.can_id)
            sc, v_h_cal, s_h_cal, _ = compute_frame_score(ab_model, s_in, v_h_cal, s_h_cal, dense_id, encoder)
            ab_cal_scores.append(sc)
        ab_cal_arr = np.array(ab_cal_scores, dtype=np.float32)

        # Step 2: Evaluate Mean FPR across all 4 authentic regimes
        encoder.reset_state()
        v_h = torch.zeros(1, CS_HIDDEN_DIM)
        s_h = torch.zeros(1, CS_HIDDEN_DIM)
        if disable_quarantine:
            ids = UnguardedOnlineACIIDS(ab_cal_arr, alpha_target=ALPHA_TARGET)
        else:
            ids = ConformalSpikeIDS(ab_cal_arr, alpha_target=ALPHA_TARGET)

        alerts_regime = 0
        total_regime_frames = 40000
        comm_counts_ab: Dict[int, int] = collections.defaultdict(int)
        comm_jumps_ab: Dict[int, List[int]] = collections.defaultdict(lambda: [0] * 8)

        for reg in ["Stationary", "Highway", "Dyno", "CrossVehicle"]:
            for f in regimes[reg]:
                dense_id = encoder.get_dense_id(f.can_id)
                is_comm = False
                if reg == "CrossVehicle":
                    if comm_counts_ab[dense_id] < 5:
                        is_comm = True
                        comm_counts_ab[dense_id] += 1
                        st = encoder.contexts[dense_id]
                        if st.valid:
                            for j in range(min(8, len(f.payload), len(st.last_payload))):
                                raw_d = abs(int(f.payload[j]) - int(st.last_payload[j]))
                                mod_d = min(raw_d, 256 - raw_d)
                                if mod_d > 15:
                                    comm_jumps_ab[dense_id][j] += 1
                                    if comm_jumps_ab[dense_id][j] >= 2 and not zero_mag:
                                        encoder.tau_max[dense_id, j] = 128

                s_in, _ = encoder.encode(f.timestamp_s, f.can_id, f.payload)
                if zero_mag:
                    s_in[27:35] = 0.0
                sc, v_n, s_n, _ = compute_frame_score(ab_model, s_in, v_h, s_h, dense_id, encoder)
                if disable_quarantine:
                    d, _, _ = ids.decide(sc)
                    q = False
                else:
                    d, _, _, q, _, _ = ids.decide(sc, dense_id)
                    if is_comm:
                        q = True

                if d == 1:
                    alerts_regime += 1

                if disable_rollback:
                    v_h, s_h = v_n, s_n
                else:
                    rolled_back = encoder.conditional_rollback(d == 1, f.timestamp_s, is_quarantined=q)
                    if not rolled_back:
                        v_h, s_h = v_n, s_n

        mean_fpr = (alerts_regime / total_regime_frames) * 100.0

        # Step 3: Evaluate TPR on Speedometer Masquerade
        speed_det = 0
        speed_stream = attack_suites["ORNL ROAD Max Speedometer Masquerade"]
        total_speed_atk = sum(1 for f in speed_stream if f.label != 'Normal')
        encoder.reset_state()
        v_h = torch.zeros(1, CS_HIDDEN_DIM)
        s_h = torch.zeros(1, CS_HIDDEN_DIM)
        if disable_quarantine:
            ids = UnguardedOnlineACIIDS(ab_cal_arr, alpha_target=ALPHA_TARGET)
        else:
            ids = ConformalSpikeIDS(ab_cal_arr, alpha_target=ALPHA_TARGET)

        for f in speed_stream:
            is_atk = (f.label != 'Normal')
            s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            if zero_mag:
                s_in[27:35] = 0.0
                tgt[16:24] = 0.0
            dense_id = encoder.get_dense_id(f.can_id)
            sc, v_n, s_n, _ = compute_frame_score(ab_model, s_in, v_h, s_h, dense_id, encoder)
            has_shock = bool(np.sum(tgt[16:24]) >= 1) if not zero_mag else False
            if disable_quarantine:
                d, _, _ = ids.decide(sc)
                q = False
            else:
                d, _, _, q, _, _ = ids.decide(sc, dense_id, has_shock=has_shock)

            if (d == 1 or q) and is_atk:
                speed_det += 1

            if disable_rollback:
                v_h, s_h = v_n, s_n
            else:
                rolled_back = encoder.conditional_rollback(d == 1, f.timestamp_s, is_quarantined=q, has_shock=has_shock)
                if not rolled_back:
                    v_h, s_h = v_n, s_n
        tpr_speed = (speed_det / max(1, total_speed_atk)) * 100.0

        # Step 4: Evaluate TPR on Correlated Masquerade
        corr_det = 0
        corr_stream = attack_suites["ORNL ROAD Correlated Masquerade"]
        total_corr_atk = sum(1 for f in corr_stream if f.label != 'Normal')
        encoder.reset_state()
        v_h = torch.zeros(1, CS_HIDDEN_DIM)
        s_h = torch.zeros(1, CS_HIDDEN_DIM)
        if disable_quarantine:
            ids = UnguardedOnlineACIIDS(ab_cal_arr, alpha_target=ALPHA_TARGET)
        else:
            ids = ConformalSpikeIDS(ab_cal_arr, alpha_target=ALPHA_TARGET)

        for f in corr_stream:
            is_atk = (f.label != 'Normal')
            s_in, tgt = encoder.encode(f.timestamp_s, f.can_id, f.payload)
            if zero_mag:
                s_in[27:35] = 0.0
                tgt[16:24] = 0.0
            dense_id = encoder.get_dense_id(f.can_id)
            sc, v_n, s_n, _ = compute_frame_score(ab_model, s_in, v_h, s_h, dense_id, encoder)
            has_shock = bool(np.sum(tgt[16:24]) >= 1) if not zero_mag else False
            if disable_quarantine:
                d, _, _ = ids.decide(sc)
                q = False
            else:
                d, _, _, q, _, _ = ids.decide(sc, dense_id, has_shock=has_shock)

            if (d == 1 or q) and is_atk:
                corr_det += 1

            if disable_rollback:
                v_h, s_h = v_n, s_n
            else:
                rolled_back = encoder.conditional_rollback(d == 1, f.timestamp_s, is_quarantined=q, has_shock=has_shock)
                if not rolled_back:
                    v_h, s_h = v_n, s_n
        tpr_corr = (corr_det / max(1, total_corr_atk)) * 100.0

        # Hardware metrics (ACs and WCET)
        active_in = 20
        active_rec = k_val
        worst_acs = (active_in * 64) + (active_rec * 64) + (active_rec * 32)
        wcet_us = (worst_acs * 2 + 1200) / 300.0

        row_dict = {
            "Configuration": name,
            "MeanFPR": mean_fpr,
            "TPRSpeedMasq": tpr_speed,
            "TPRCorrMasq": tpr_corr,
            "WorstACs": worst_acs,
            "WCET_us": wcet_us
        }
        ablation_rows.append(row_dict)
        print(f"  {name:38s} | Mean FPR: {mean_fpr:5.2f}% | SpeedMasq: {tpr_speed:5.2f}% | CorrMasq: {tpr_corr:5.2f}% | ACs: {worst_acs:5d} | WCET: {wcet_us:5.2f} us", flush=True)

    return ablation_rows


def run_pulse_attack_simulation(
    model: IDConditionedKWtaSNN,
    encoder: PerIDNeuromorphicEncoder,
    benign_frames: List[CANFrame],
    cal_scores: np.ndarray,
    num_frames: int = 2000
) -> Dict[str, np.ndarray]:
    print("\n============================================================================", flush=True)
    print("FIGURE 2 BENCHMARK: INTERLEAVED PULSE ATTACK DEFENSE SIMULATION TRACE", flush=True)
    print("============================================================================", flush=True)

    m3_aci = UnguardedOnlineACIIDS(cal_scores, alpha_target=ALPHA_TARGET)
    m4_conformal = ConformalSpikeIDS(cal_scores, alpha_target=ALPHA_TARGET)

    # 1. Warm-up encoder, hidden states, and IDS trackers on 200 benign frames so rho_alert starts at 0!
    encoder.reset_state()
    v_warm = torch.zeros(1, CS_HIDDEN_DIM)
    s_warm = torch.zeros(1, CS_HIDDEN_DIM)
    for w in range(200):
        bf = benign_frames[w % len(benign_frames)]
        s_in, _ = encoder.encode(w * 0.0005, bf.can_id, bf.payload)
        dense_id = encoder.get_dense_id(bf.can_id)
        sc, v_warm, s_warm, _ = compute_frame_score(model, s_in, v_warm, s_warm, dense_id, encoder)
        m3_aci.decide(sc)
        m4_conformal.decide(sc, dense_id)

    ground_truth = np.zeros(num_frames, dtype=int)
    aci_alphas = np.zeros(num_frames, dtype=float)
    aci_thresholds = np.zeros(num_frames, dtype=float)
    aci_alerts = np.zeros(num_frames, dtype=int)

    cs_alphas = np.zeros(num_frames, dtype=float)
    cs_thresholds = np.zeros(num_frames, dtype=float)
    cs_alerts = np.zeros(num_frames, dtype=int)
    cs_quarantines = np.zeros(num_frames, dtype=int)
    cs_alert_densities = np.zeros(num_frames, dtype=float)

    v_cs = v_warm.clone()
    s_cs = s_warm.clone()
    v_aci = v_warm.clone()
    s_aci = s_warm.clone()

    target_dense_id = encoder.get_dense_id(0x6E0)
    t_curr = 0.100
    for k in range(num_frames):
        t_curr += 0.0005
        is_attack = False
        if 400 <= k < 1500:
            if (k % 3) != 0:  # 2-on-1-off pulse attack
                is_attack = True

        ground_truth[k] = 1 if is_attack else 0
        base_f = benign_frames[(200 + k) % len(benign_frames)]
        cid = 0x6E0 if is_attack else base_f.can_id
        p = bytearray(base_f.payload.ljust(8, b'\x00'))

        if is_attack:
            p[1] = 0xFF

        s_in, _ = encoder.encode(t_curr, cid, bytes(p))
        dense_id = encoder.get_dense_id(cid)

        # 1. Run Unguarded ACI
        sc_aci, v_n_aci, s_n_aci, _ = compute_frame_score(model, s_in, v_aci, s_aci, dense_id, encoder)
        d_aci, th_aci, a_aci = m3_aci.decide(sc_aci)
        aci_alerts[k] = d_aci
        aci_thresholds[k] = th_aci
        aci_alphas[k] = a_aci
        v_aci, s_aci = v_n_aci, s_n_aci

        # 2. Run ConformalSpike
        sc_cs, v_n_cs, s_n_cs, _ = compute_frame_score(model, s_in, v_cs, s_cs, dense_id, encoder)
        d_cs, th_cs, a_cs, q_cs, rho_glob, rho_id = m4_conformal.decide(sc_cs, dense_id)
        cs_alerts[k] = d_cs
        cs_thresholds[k] = th_cs
        cs_alphas[k] = a_cs
        cs_quarantines[k] = 1 if q_cs else 0
        cs_alert_densities[k] = float(m4_conformal.alert_density_id[target_dense_id])

        rolled_back = encoder.conditional_rollback(d_cs == 1, t_curr, is_quarantined=q_cs)
        if not rolled_back:
            v_cs, s_cs = v_n_cs, s_n_cs

    print("  Pulse attack simulation trace complete.", flush=True)
    return {
        "ground_truth": ground_truth,
        "aci_alphas": aci_alphas,
        "aci_thresholds": aci_thresholds,
        "aci_alerts": aci_alerts,
        "cs_alphas": cs_alphas,
        "cs_thresholds": cs_thresholds,
        "cs_alerts": cs_alerts,
        "cs_quarantines": cs_quarantines,
        "cs_alert_densities": cs_alert_densities
    }
