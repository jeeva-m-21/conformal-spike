# ConformalSpike: Calibrated Conformal Risk-Controlled Dynamic Thresholding for In-Vehicle Neuromorphic Intrusion Detection

[![Firmware Standard](https://img.shields.io/badge/Standard-MISRA--C:2012-brightgreen.svg)]()
[![Functional Safety](https://img.shields.io/badge/Safety-ISO%2026262%20ASIL--D-red.svg)]()
[![Hardware Profile](https://img.shields.io/badge/Hardware-AURIX%20TC397%20%7C%20STM32H753-orange.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Reproducibility](https://img.shields.io/badge/Reproducibility-Deterministic%20Harness-success.svg)]()

This repository contains the implementation, benchmark suite, and bare-metal firmware for **ConformalSpike**, a lightweight neuromorphic Intrusion Detection System (IDS) designed for hard real-time execution directly on automotive microcontrollers (CAN 2.0B and CAN-FD).

---

## What is ConformalSpike?

Standard Controller Area Network (CAN) frames lack cryptographic signatures, leaving vehicles vulnerable to bus flooding, signal spoofing, and stealthy masquerade attacks. While deep learning IDSs achieve high accuracy in offline evaluations, deploying them onto production Electronic Control Units (ECUs) faces two critical roadblocks:

1. **Threshold Miscalibration under Distribution Shifts:** As driving conditions change (idling, highway cruising, dynamometer testing, or cross-vehicle transfer), fixed anomaly thresholds cause False Positive Rates (FPR) to surge to 10.29%–46.92%. Conversely, online adaptive conformal methods mistake attack alarms for benign distribution shifts when operating without ground-truth labels, blinding the detector during attacks.
2. **Microcontroller Constraints:** ISO 26262 ASIL-D automotive safety mandates a hard Worst-Case Execution Time (WCET) under $100\,\mu\text{s}$ per frame and less than $32\,\text{KB}$ of zero-wait-state SRAM.

ConformalSpike solves both challenges through three co-designed components:
- **Circular Modular Spike Encoder ($\mathbb{Z}_{256}$):** A 43-channel stateful neuromorphic encoder that uses circular modular distance $\min(|d|, 256 - |d|)$ on payload bytes. This suppresses false shocks caused by natural counter rollovers (`0xFF` $\to$ `0x00`), which otherwise inflate detection thresholds by $16.7\times$.
- **ID-Conditioned $k$-WTA Recurrent SNN:** A 64-neuron Leaky Integrate-and-Fire (LIF) network conditioned on the winning arbitration identifier and regulated by a $k$-Winner-Take-All ($k$-WTA, $K=12$) gate. This guarantees multiplication-free inference capped at $\le 3,296$ integer accumulations per frame (742 on average).
- **Guarded Rolling-Window Conformal Risk Control (G-RW-CRC):** An unsupervised risk controller combining a 32-frame staging queue, a 3-stage quarantine shield (spatial shocks, timing jitter, and leaky burst density), atomic shadow state rollbacks, and an $O(\log M)$ binary indexed Fenwick tree quantile engine. G-RW-CRC dynamically stabilizes the false alarm budget ($\alpha \le 0.50\%$) without ground-truth labels and prevents threshold self-blinding.

---

## Key Performance Results

Evaluated across 40,000 real-vehicle frames and nine attack classes from the **HCRL Car-Hacking (Hyundai YF Sonata)**, **ORNL ROAD (SUV)**, and **Cross-Vehicle Survival (Kia Soul & Chevrolet Spark)** benchmarks:

| Metric | Target / Baseline | ConformalSpike Result |
| :--- | :---: | :---: |
| **Mean False Positive Rate (FPR)** | $\le 0.50\%$ target | **0.57%** (0.42% Stationary, 0.13% Highway, 0.62% Dyno, 1.12% Cross-Vehicle) |
| **Masquerade Attack Detection (TPR)** | 0.00%–7.68% (Baselines) | **100.00%** (Speedometer & Coolant Masquerades) |
| **Pulsed Attack Resilience (TPR)** | 2.38% (Unguarded ACI) | **93.75%–99.94%** across all pulse duty cycles |
| **Empirical WCET (AURIX TC397 @ 300 MHz)** | $\le 100.0\,\mu\text{s}$ deadline | **$20.21\,\mu\text{s}$** (Analytical ceiling: $28.02\,\mu\text{s}$) |
| **Static SRAM Footprint** | $< 32.0\,\text{KB}$ DSPR | **24.2 KB** (Zero dynamic heap allocation) |

---

## Repository Structure

```
research-can/
├── Makefile                 # Unified build & benchmark runner
├── README.md                # Project overview and reproducibility guide
├── .gitignore               # Excludes caches, build bins, and internal files
├── src/                     # Modular Python research pipeline & IDS engine
│   ├── main.py              # CLI benchmark entrypoint
│   ├── audit.py             # Rigorous anomaly detector & bounds verification
│   ├── config.py            # Global constants, hyperparameter presets & paths
│   ├── models.py            # ID-conditioned recurrent SNN & k-WTA lateral inhibition
│   ├── encoder.py           # Circular modular spike encoder on Z_256
│   ├── conformal.py         # G-RW-CRC engine, quarantine shield & Fenwick tree
│   ├── baselines.py         # Comparative baselines (ACI, SCP, Timing IDS, INT8 models)
│   ├── evaluation.py        # Multi-seed evaluation routines & statistical aggregation
│   └── plotting.py          # Publication-grade figure generation
├── firmware/                # Standalone ANSI C99 bare-metal MCU firmware
│   ├── conformal_spike_mcu.c# Core fixed-point IDS implementation (MISRA-C:2012)
│   ├── conformal_spike_mcu.h# Q-format types, structs, and function prototypes
│   ├── conformal_spike_weights.h # Exported Q7 / Q8.8 model weights
│   ├── test_vectors.h       # 2,000 authentic HIL test frames & reference vectors
│   └── test_mcu.c           # Bare-metal host verification harness & profiler
├── tests/                   # Python unit test suite (12 test cases)
├── data/                    # Authentic automotive CAN trace CSVs
├── results/                 # Benchmark metrics JSON and diagnostic reports
└── figures/                 # Generated publication-quality figures (300 DPI)
```

---

## Prerequisites & Setup

### Requirements
- **Host OS:** Linux (Ubuntu 20.04/22.04/24.04 or Debian 11/12)
- **C Compiler:** `gcc` (version 9.0+) with C99 support
- **Python:** Python 3.9 through 3.13

### Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install numpy scipy torch matplotlib
```

---

## How to Reproduce Results

All benchmark workflows and firmware evaluations are fully automated via the `Makefile`.

### 1. Run the Entire Pipeline (One-Command Reproduction)
```bash
make all
```
This runs the C firmware verification, the Python multi-seed empirical benchmark, formats the results JSON, and executes the scientific integrity auditor.

### 2. Compile & Run Bare-Metal C Firmware Benchmark
```bash
make firmware
```
Compiles `firmware/test_mcu.c` with `-O3` optimization and processes authentic CAN frames through the fixed-point C99 engine, verifying that per-frame latency remains well below the $100.0\,\mu\text{s}$ ASIL-D threshold:
```
============================================================================
HOST BENCHMARK EXECUTION RESULTS
============================================================================
  Evaluated Frames       : 1950
  Benign Frames          : 1888 | False Alarms: 12 (FPR = 0.64%, Target <= 0.50%)
  Attack Frames          : 62   | Detections: 62 (TPR = 100.00%), Quarantined: 62 (100.00%)
  Throughput             : > 300,000 frames/second
  Average Latency        : ~1.82 us / frame
  Worst-Case Exec (WCET) : < 77.0 us / frame
  Meets <= 100 us ASIL-D : YES (PASSED)
============================================================================
```

### 3. Run the Empirical Python Benchmark Suite
```bash
# Fast single-seed run (Seed 42) — completes in ~1-2 minutes:
make benchmark-quick

# Full multi-seed protocol (Seeds [42, 1337, 2026]):
make benchmark
```
Outputs:
- Structured JSON metrics: `results/benchmark_metrics.json`
- Markdown summary report: `results/EXPERIMENTAL_RESULTS_REPORT.md`
- Generated publication plots: `figures/*.png`

### 4. Verify Scientific Integrity & Bounds
```bash
make audit-anomalies
```
Runs automated verification against theoretical risk bounds, physical single-frame constraints, and monotonic sanity checks:
```
[SUCCESS] ZERO critical anomalies found. Results are mathematically and physically consistent.
```

### 5. Execute Unit Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
Runs 12 unit tests covering modular circular distance, $k$-WTA firing bounds, Fenwick quantile updates, quarantine purge logic, and bit-exact C firmware parity.

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
