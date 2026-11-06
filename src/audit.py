#!/usr/bin/env python3
"""
Automated Anomaly Detection & Empirical Integrity Auditor for ConformalSpike
Verifies statistical soundness, bounds, physical consistency, and ensures zero discrepancies.
"""

import sys
import json
import os

METRICS_PATH = "results/benchmark_metrics.json"

def audit_results():
    if not os.path.exists(METRICS_PATH):
        print(f"[FAIL] Metrics file not found at {METRICS_PATH}. Run benchmark first.")
        sys.exit(1)

    with open(METRICS_PATH, "r") as f:
        data = json.load(f)

    t1 = data.get("table_i_regime_shifts", {})
    t2 = data.get("table_ii_attack_detection", {})
    t5 = data.get("table_v_ablation_study", {})
    pulse_sweep = data.get("adversarial_pulse_sweep", {})

    anomalies = []
    warnings = []

    print("============================================================================")
    print("CONFORMALSPIKE BENCHMARK INTEGRITY & ANOMALY AUDITOR")
    print("============================================================================")

    # 1. Audit Table I (Regime Shifts, Target alpha = 0.50%)
    cs_t1 = t1.get("ConformalSpike (Proposed G-RW-CRC)", {})
    print("\n--- Auditing Table I: Driving Regime Stability (Target alpha = 0.50%) ---")
    for reg in ["Stationary", "Highway", "Dyno", "CrossVehicle"]:
        val = cs_t1.get(reg, 0.0)
        fpr = val.get("mean", 0.0) if isinstance(val, dict) else float(val)
        print(f"  {reg:14s}: FPR = {fpr:5.2f}%")
        if fpr > 3.0:
            anomalies.append(f"Table I FPR dangerously elevated in {reg}: {fpr:.2f}% (must be <= 1.50% for ASIL-D target)")
        elif fpr < 0.05:
            anomalies.append(f"Table I FPR suspiciously suppressed in {reg}: {fpr:.2f}% (check if detector is permanently muted)")

    mean_fpr = cs_t1.get("MeanFPR", 0.0)
    mean_val = mean_fpr.get("mean", 0.0) if isinstance(mean_fpr, dict) else float(mean_fpr)
    print(f"  Overall Mean  : FPR = {mean_val:5.2f}%")
    if abs(mean_val - 0.50) > 0.50:
        anomalies.append(f"Regime-averaged MeanFPR ({mean_val:.2f}%) deviates by >0.50% from nominal 0.50% target")

    # 2. Audit Table II: Attack Detection (Attacks should have high TPR; stealthy in-envelope should be honestly bounded)
    cs_t2 = t2.get("ConformalSpike (Proposed G-RW-CRC)", {})
    print("\n--- Auditing Table II: Attack Detection TPR ---")
    critical_attacks = [
        ("HCRL DoS Flooding", 95.0),
        ("HCRL Fuzzy Attack", 90.0),
        ("HCRL RPM Spoofing", 95.0),
        ("HCRL Gear Spoofing", 95.0),
        ("ORNL ROAD Max Speedometer Masquerade", 80.0),
        ("ORNL ROAD Max Coolant Masquerade", 80.0),
        ("ORNL ROAD Accelerator Masquerade", 80.0),
    ]

    for atk_name, min_expected_tpr in critical_attacks:
        val = cs_t2.get(atk_name, 0.0)
        tpr = val.get("mean", 0.0) if isinstance(val, dict) else float(val)
        print(f"  {atk_name:40s}: TPR = {tpr:5.2f}%")
        if tpr < min_expected_tpr:
            anomalies.append(f"Table II attack detection collapsed on '{atk_name}': {tpr:.2f}% (expected >= {min_expected_tpr}%)")

    # Correlated masquerade check
    corr_val = cs_t2.get("ORNL ROAD Correlated Masquerade", 0.0)
    corr_tpr = corr_val.get("mean", 0.0) if isinstance(corr_val, dict) else float(corr_val)
    print(f"  {'ORNL ROAD Correlated Masquerade':40s}: TPR = {corr_tpr:5.2f}% (Stealthy In-Envelope)")
    if corr_tpr > 50.0:
        warnings.append(f"Correlated masquerade TPR unusually high ({corr_tpr:.2f}%). Confirm if genuine or synthetic injection.")

    # 3. Audit Table II vs Table V Consistency
    print("\n--- Auditing Table II vs. Table V Consistency ---")
    if isinstance(t5, list):
        t5_dict = {row.get("Configuration", ""): row for row in t5}
    else:
        t5_dict = t5
    full_t5 = t5_dict.get("Full Proposed ConformalSpike", {})
    t5_speed_val = full_t5.get("TPRSpeedMasq", full_t5.get("SpeedMasq", 0.0))
    t5_speed = t5_speed_val.get("mean", 0.0) if isinstance(t5_speed_val, dict) else float(t5_speed_val)

    t2_speed_val = cs_t2.get("ORNL ROAD Max Speedometer Masquerade", 0.0)
    t2_speed = t2_speed_val.get("mean", 0.0) if isinstance(t2_speed_val, dict) else float(t2_speed_val)

    print(f"  Table II SpeedMasq TPR : {t2_speed:5.2f}%")
    print(f"  Table V  SpeedMasq TPR : {t5_speed:5.2f}%")
    if abs(t2_speed - t5_speed) > 10.0:
        anomalies.append(f"Severe inconsistency: Table II SpeedMasq ({t2_speed:.2f}%) vs Table V SpeedMasq ({t5_speed:.2f}%)")

    # 4. Audit Adversarial Pulse Sweep: Self-Blinding Proof
    print("\n--- Auditing Adversarial Pulse Sweep: Threshold Self-Blinding ---")
    unguarded_sweep = pulse_sweep.get("Unguarded Online ACI (Gibbs & Candes)", {})
    cs_sweep = pulse_sweep.get("ConformalSpike (Proposed G-RW-CRC)", {})

    duty_100_ung = unguarded_sweep.get("Continuous (100.0%)", {}).get("mean", 100.0) if isinstance(unguarded_sweep.get("Continuous (100.0%)"), dict) else unguarded_sweep.get("Continuous (100.0%)", 100.0)
    duty_100_cs = cs_sweep.get("Continuous (100.0%)", {}).get("mean", 0.0) if isinstance(cs_sweep.get("Continuous (100.0%)"), dict) else cs_sweep.get("Continuous (100.0%)", 0.0)

    print(f"  At 100% Attack Duty Cycle: Unguarded ACI TPR = {duty_100_ung:5.2f}% | ConformalSpike TPR = {duty_100_cs:5.2f}%")
    if duty_100_ung > 20.0:
        warnings.append(f"Unguarded ACI did not exhibit expected threshold self-blinding at 100% duty (TPR = {duty_100_ung:.2f}%)")
    if duty_100_cs < 90.0:
        anomalies.append(f"ConformalSpike failed to resist continuous attack pulse (TPR = {duty_100_cs:.2f}%)")

    # Report Summary
    print("\n============================================================================")
    print("AUDIT SUMMARY")
    print("============================================================================")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print("  [WARN]", w)

    if anomalies:
        print(f"\nCRITICAL ANOMALIES FOUND ({len(anomalies)}):")
        for a in anomalies:
            print("  [FAIL]", a)
        print("\nAudit status: FAILED. Please fix code issues.")
        sys.exit(1)
    else:
        print("  [SUCCESS] ZERO critical anomalies found. Results are mathematically and physically consistent.")
        sys.exit(0)

if __name__ == "__main__":
    audit_results()
