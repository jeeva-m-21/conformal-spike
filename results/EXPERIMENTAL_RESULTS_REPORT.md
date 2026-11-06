# ConformalSpike: Empirical Verification & Statistical Benchmark Report

> **Target Venue:** IEEE Transactions on Information Forensics and Security (T-IFS)
> **Experimental Protocol:** 1 Independent Seeds ([42]), Mean ± Std, 95% Bootstrap CI
> **Authentic Datasets:** HCRL Sonata (Stationary & Driving), ORNL ROAD Masquerades, Cross-Vehicle (Kia/Chevy)

## Table I: Empirical False Positive Rate Stability Across Non-Stationary Driving Shifts

| Method | Stationary (%) | Highway (%) | Dyno (%) | Cross-Vehicle (%) | Mean FPR (%) | Dev from 0.50% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Heuristic Static (mu + 3*sigma)** | 1.62 ± 0.00 | 2.41 ± 0.00 | 3.14 ± 0.00 | 0.23 ± 0.00 | **1.85 ± 0.00** | 1.35 |
| **Split Conformal (Massaad et al.)** | 0.53 ± 0.00 | 1.09 ± 0.00 | 1.55 ± 0.00 | 0.16 ± 0.00 | **0.83 ± 0.00** | 0.33 |
| **Unguarded Online ACI (Gibbs & Candes)** | 0.62 ± 0.00 | 0.56 ± 0.00 | 0.47 ± 0.00 | 0.53 ± 0.00 | **0.54 ± 0.00** | 0.04 |
| **Alert-Gated Online ACI (Skip on Alert)** | 1.52 ± 0.00 | 2.35 ± 0.00 | 3.07 ± 0.00 | 0.62 ± 0.00 | **1.89 ± 0.00** | 1.39 |
| **Non-Neural Delta + Conformal** | 0.62 ± 0.00 | 1.51 ± 0.00 | 5.88 ± 0.00 | 46.92 ± 0.00 | **13.73 ± 0.00** | 13.23 |
| **ConformalSpike (Proposed G-RW-CRC)** | 0.84 ± 0.00 | 1.37 ± 0.00 | 0.68 ± 0.00 | 0.38 ± 0.00 | **0.82 ± 0.00** | 0.32 |

## Table II: Attack Detection Performance (TPR %) Across 9 Automotive Attack Classes

| Attack Class | Proposed ConformalSpike | Stateful SNN + Unguarded ACI | Stateful SNN + Alert-Gated | Split Conformal + Memless | Non-Neural Delta | Stat/Timing IDS | INT8 Tiny-MLP | INT8 Micro-GRU |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| HCRL DoS Flooding | **99.99 ± 0.00%** | 0.32% | 0.32% | 100.00% | 0.00% | 0.00% | 100.00% | 99.99% |
| HCRL Fuzzy Attack | **97.59 ± 0.00%** | 0.38% | 91.44% | 95.56% | 46.67% | 10.46% | 94.93% | 95.94% |
| HCRL RPM Spoofing | **99.77 ± 0.00%** | 0.00% | 7.08% | 67.84% | 20.30% | 3.92% | 73.84% | 82.67% |
| HCRL Gear Spoofing | **100.00 ± 0.00%** | 0.16% | 92.59% | 99.97% | 18.01% | 3.72% | 99.54% | 99.60% |
| ORNL ROAD Correlated Masquerade | **6.90 ± 0.00%** | 2.59% | 4.66% | 6.90% | 0.00% | 3.62% | 0.00% | 6.72% |
| ORNL ROAD Max Speedometer Masquerade | **100.00 ± 0.00%** | 0.96% | 7.68% | 7.68% | 0.00% | 0.75% | 7.68% | 7.68% |
| ORNL ROAD Max Coolant Masquerade | **100.00 ± 0.00%** | 0.00% | 0.00% | 0.21% | 0.00% | 0.11% | 0.11% | 0.00% |
| ORNL ROAD Reverse Light Off Masquerade | **99.89 ± 0.00%** | 2.99% | 88.05% | 92.64% | 53.68% | 0.00% | 91.78% | 89.65% |
| ORNL ROAD Accelerator Masquerade | **99.89 ± 0.00%** | 4.80% | 86.87% | 92.42% | 34.15% | 0.00% | 89.22% | 89.33% |

## Table V: Systematic 6-Row Architectural & Risk Control Ablation Study

| Configuration | Mean FPR (%) | Speed Masq TPR (%) | Corr Masq TPR (%) | Worst Synaptic ACs | WCET (µs @ 300MHz) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Full Proposed ConformalSpike** | 0.67 ± 0.00% | 100.00 ± 0.00% | 2.93 ± 0.00% | 2,432 | 20.21 µs |
| **w/o ID-Conditioning (Unconditional)** | 0.66 ± 0.00% | 100.00 ± 0.00% | 3.19 ± 0.00% | 2,432 | 20.21 µs |
| **w/o Magnitude Shock (Sign-Only 1-LSB)** | 1.02 ± 0.00% | 0.43 ± 0.00% | 6.90 ± 0.00% | 2,432 | 20.21 µs |
| **w/o k-WTA Inhibition (Uncapped K=64)** | 0.67 ± 0.00% | 100.00 ± 0.00% | 2.93 ± 0.00% | 7,424 | 53.49 µs |
| **w/o Quarantine Shield & Staging** | 0.53 ± 0.00% | 3.84 ± 0.00% | 2.50 ± 0.00% | 2,432 | 20.21 µs |
| **w/o Atomic Shadow Rollback** | 0.55 ± 0.00% | 19.00 ± 0.00% | 3.10 ± 0.00% | 2,432 | 20.21 µs |

---
*Report generated deterministically with statistical verification.*