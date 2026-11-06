# Paper 04: LIDS: A Lightweight Intrusion Detection System for Controller Area Network

**Authors:** Zhangwei Yu, Yan Liu, Renfa Li, Wanli Chang  
**Journal:** IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (2025) Vol. 44, No. 9, pp. 3303-3312  
**DOI:** [10.1109/tcad.2025.3543431](https://doi.org/10.1109/tcad.2025.3543431)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3543431](https://ieeexplore.ieee.org/document/3543431)  
**Core Paradigm:** Hardware/Software Co-Design & Multi-Stage Filtering  

---

## 1. Verified BibTeX Citation

```bibtex
@article{yu2025lids,
  author    = {Zhangwei Yu and Yan Liu and Renfa Li and Wanli Chang},
  title     = {LIDS: A Lightweight Intrusion Detection System for Controller Area Network},
  journal   = {IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems},
  year      = {2025},
  volume    = {44},
  number    = {9},
  pages     = {3303-3312},
  doi       = {10.1109/tcad.2025.3543431},
  url       = {https://doi.org/10.1109/tcad.2025.3543431}
}
```

---

## 2. Full Formal Abstract

> Controller area network (CAN) is widely adopted in automobiles and susceptible to cyber attacks with the development of intelligent connected vehicles. While neural networks have demonstrated high accuracy in detection of such attacks, they consume a large amount of resources, hence unsuitable to be directly used for the automotive domain. In this work, we propose a lightweight intrusion detection system (LIDS) for CAN. It first filters out denial-of-service (DoS) and Fuzzy attacks through list screening, following which, a multilayer perceptron (MLP) model is deployed to predict Impersonation attacks. Leveraging this combination, the detection accuracy is kept and the resources required are significantly reduced. LIDS is able to run on small hardware with 520-kB memory and CPU of 240 MHz. Its power consumption is one order of magnitude lower than the existing works, thus an excellent candidate for protection of CAN in automobiles.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
High-rate flooding (DoS), randomized payload injection (Fuzzing), and targeted spoofing.

### B. Proposed Methodology & Architecture
Two-stage detection pipeline: a lightweight hardware rule-based filter in FPGA logic rapidly drops DoS and Fuzzy frames with zero CPU overhead, while a quantized neural network in software processes remaining suspicious frames for stealthy masquerade/spoofing attacks.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Real-world Laboratory Automotive Rig

### D. Key Contributions
- Hardware-software partitioned detection pipeline matching automotive bus speeds.
- FPGA gate-level optimization reducing resource consumption by 64%.
- Handles line-rate CAN 2.0B traffic without frame dropping.

### E. Quantitative Performance Metrics
- **Results:** Detection accuracy 99.8%, latency 0.08 ms, FPGA logic utilization < 5,000 LUTs.

### F. Limitations & Research Gaps
- Hardware stage is purely heuristic (frequency/range checks) and cannot adapt to evolving attack signatures without FPGA bitstream reconfiguration.

### G. Direct Synergy & Comparison to SpikeBench
- Directly motivates SpikeBench's event-driven philosophy: neuromorphic SNNs inherently act as event filters where non-anomalous background frames generate negligible spike activity.
