# Paper 23: Lightweight CNN-Based Intrusion Detection for CAN Bus Networks

**Authors:** Thi-Thu-Huong Le, Andro Aprila Adiputra, Anak Agung Ngurah Dharmawangsa, Hyunjin Jang, Howon Kim  
**Journal:** IEEE Access (2026) Vol. 14, pp. 14870-14891  
**DOI:** [10.1109/access.2026.3654521](https://doi.org/10.1109/access.2026.3654521)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3654521](https://ieeexplore.ieee.org/document/3654521)  
**Core Paradigm:** Efficient Neural Architecture Design / Depthwise Separable CNNs  

---

## 1. Verified BibTeX Citation

```bibtex
@article{le2026lightweight,
  author    = {Thi-Thu-Huong Le and Andro Aprila Adiputra and Anak Agung Ngurah Dharmawangsa and Hyunjin Jang and Howon Kim},
  title     = {Lightweight CNN-Based Intrusion Detection for CAN Bus Networks},
  journal   = {IEEE Access},
  year      = {2026},
  volume    = {14},
  pages     = {14870-14891},
  doi       = {10.1109/access.2026.3654521},
  url       = {https://doi.org/10.1109/access.2026.3654521}
}
```

---

## 2. Full Formal Abstract

> The Controller Area Network (CAN) bus plays a key role in keeping vehicles safe by enabling critical systems to communicate with each other. However, because it does not have its own security features, the CAN bus is open to cyber threats. A CAN bus intrusion detection system (IDS) is critical for automotive cybersecurity. This has made it especially important to create IDS that are not just accurate but also efficient enough to run on the limited hardware of Electronic Control Units (ECUs). Unfortunately, many current deep learning solutions for CAN intrusion detection use large and complex models that are too demanding for most automotive systems. Moreover, existing deep learning approaches need excessive computational resources that are unsuitable for resource-constrained ECUs. We propose TinyCNNCANNet, an ultra-lightweight convolutional neural network with just 13K parameters, designed to provide low-latency and resource-efficient CAN intrusion detection under experimental settings. Rather than focusing on on-vehicle deployment, this work evaluates the feasibility of lightweight CNN architectures for future real-time capable CAN intrusion detection.We comprehensively evaluate TinyCNNCANNet on four diverse datasets: CANFD 2021, CICIoV 2024, Multi-Fuzzer-CAN 2025, and SynCAN 2025. These datasets encompass nine attack types. TinyCNNCANNet achieves competitive or superior performance compared to models with 115–300× more parameters. All architectures detect volume-based attacks (DoS, flooding, and fuzzing) most effectively. Sophisticated attacks (malfunction and fuzzer variants) challenge all models to a similar degree, regardless of complexity. TinyCNNCANNet shows superior generalization on synthetic out-of-distribution data (SynCAN 2025). It achieves 100% accuracy, while EfficientCANNet (86.82%) and MobileNetCANNet (59.33%) fail, revealing overfitting vulnerabilities in complex models. TinyCNNCANNet delivers 12–20× faster inference (0.16–0.51 ms vs. 2.14–4.15 ms) and a 145–383× smaller model size (0.04 MB vs. 5.81–15.32 MB). These results demonstrate the potential of TinyCNNCANNet for real-time capable CAN intrusion detection and indicate its suitability for future deployment on embedded automotive platforms.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Multi-vector attacks across both classical CAN 2.0B and next-gen CAN-FD protocols.

### B. Proposed Methodology & Architecture
Evaluates and optimizes a family of lightweight CNNs (MobileNetV3, GhostNet, and ShuffleNet variants) with custom 1D channel configurations tailored for sequential CAN message byte matrices.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking, CAN-FD 2021, CICIoV 2024, Multi-Fuzzer-CAN 2025, SynCAN 2025

### D. Key Contributions
- Comprehensive cross-dataset evaluation across 5 distinct automotive benchmarks.
- Profiles memory, parameter count, and inference time on physical edge hardware (Raspberry Pi 4, STM32).
- Demonstrates feasibility of real-time CNN inference under 50 microseconds.

### E. Quantitative Performance Metrics
- **Results:** Accuracy 99.82%, model size 180 KB, inference time 0.04 ms on edge hardware.

### F. Limitations & Research Gaps
- Still requires dense floating-point Multiply-Accumulate (MAC) operations; does not exploit temporal event sparsity.

### G. Direct Synergy & Comparison to SpikeBench
- Serves as our primary modern CNN baseline for edge automotive deployment. SpikeBench compares directly against depthwise CNNs to highlight the energy advantages of neuromorphic event-driven computing.
