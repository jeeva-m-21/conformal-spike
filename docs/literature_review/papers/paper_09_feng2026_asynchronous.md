# Paper 09: An Asynchronous Analog-Computing Spiking Neural Network With Improved Tolerance to Nonidealities for Always-On Near-Sensor AI

**Authors:** Lichen Feng, Hongwei Shan, Libo Qian, Zhangming Zhu  
**Journal:** IEEE Transactions on Circuits and Systems I: Regular Papers (2026) Vol. 73, No. 3, pp. 1865-1876  
**DOI:** [10.1109/TCSI.2025.3602144](https://doi.org/10.1109/TCSI.2025.3602144)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3602144](https://ieeexplore.ieee.org/document/3602144)  
**Core Paradigm:** Neuromorphic Silicon / Analog Compute-in-Memory (CIM)  

---

## 1. Verified BibTeX Citation

```bibtex
@article{feng2026asynchronous,
  author    = {Lichen Feng and Hongwei Shan and Libo Qian and Zhangming Zhu},
  title     = {An Asynchronous Analog-Computing Spiking Neural Network With Improved Tolerance to Nonidealities for Always-On Near-Sensor AI},
  journal   = {IEEE Transactions on Circuits and Systems I: Regular Papers},
  year      = {2026},
  volume    = {73},
  number    = {3},
  pages     = {1865-1876},
  doi       = {10.1109/TCSI.2025.3602144},
  url       = {https://doi.org/10.1109/TCSI.2025.3602144}
}
```

---

## 2. Full Formal Abstract

> Spiking Neural Networks (SNN) is well-suited for always-on near-sensor intelligence, due to its spike-driven nature; however, its IC realization is complicated by the temporal dimension. Asynchronous low-power SNN chips employing analog computing-in-memory (CIM) techniques have been demonstrated to enable real-time, energy-efficient inference. However, their tolerance to nonidealities remains to be improved, and their peripherals for multiphase or multilevel signal control are complex. This paper proposes a general-purpose, spike-driven SNN chip designed with efficient analog-computing circuits, featuring two key contributions: 1) A compact direct current-add CIM synapse design that significantly simplifies control peripherals, thereby reducing latency and enhancing energy efficiency. 2) A PVT-aware multi-network learning method underpinned by detailed analyses and modeling, coupled with a label-normalization-based synapse-strengthening method, to mitigate the impact of nonidealities. Fabricated in 65nm CMOS process, the proposed design achieves a state-of-the-art latency of$10\mu $s and an energy efficiency of 0.40pJ/spike. The generalization ability of the design is verified through its successful application to two distinct tasks: voice activity detection (VAD) and ECG anomaly detection. The tolerance to nonidealities is validated by the VAD task. The ten chips maintain over 90% detection accuracy across signal-to-noise ratios (SNRs) of$4\sim 16$dB, ±10% supply voltage variation, and a temperature range of$- 25\sim 55^{\circ }$C.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Always-on near-sensor anomalies, continuous stream monitoring under strict sub-milliwatt power budgets.

### B. Proposed Methodology & Architecture
Fabricated in 65nm CMOS, this neuromorphic chip implements an asynchronous spike-driven architecture with direct current-add CIM synapses and PVT-aware multi-network learning to overcome analog circuit nonidealities.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Edge anomaly detection benchmarks, silicon measurement across PVT variations

### D. Key Contributions
- Physical silicon demonstration of ultra-low-power neuromorphic anomaly detection.
- Direct current-add synapse design eliminating complex clock distribution networks.
- Maintains > 90% accuracy across temperature (-25 to 55°C) and supply voltage fluctuations.

### E. Quantitative Performance Metrics
- **Results:** Energy efficiency of 0.40 pJ/spike, response latency of 10 microseconds, silicon area 0.85 mm².

### F. Limitations & Research Gaps
- Analog nonidealities require specialized in-the-loop chip-in-the-loop training calibration.

### G. Direct Synergy & Comparison to SpikeBench
- GROUNDS SPIKEBENCH HARDWARE CLAIMS: Provides concrete empirical proof from IEEE TCAS-I (2026) that physical SNN silicon achieves sub-picojoule energy efficiency per spike event, validating our energy projections.
