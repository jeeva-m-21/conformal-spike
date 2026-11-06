# Paper 02: Efficient Intrusion Detection for In-Vehicle Networks Using Knowledge Distillation From BERT to CNN-BiLSTM

**Authors:** Sifan Li, Yue Cao, Guojun Peng, Meng Li, Wei Sun, Luan Chen  
**Journal:** IEEE Transactions on Information Forensics and Security (2025) Vol. 20, pp. 6398-6412  
**DOI:** [10.1109/tifs.2025.3581117](https://doi.org/10.1109/tifs.2025.3581117)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3581117](https://ieeexplore.ieee.org/document/3581117)  
**Core Paradigm:** Transformer Pretraining & Knowledge Distillation  

---

## 1. Verified BibTeX Citation

```bibtex
@article{li2025efficient,
  author    = {Sifan Li and Yue Cao and Guojun Peng and Meng Li and Wei Sun and Luan Chen},
  title     = {Efficient Intrusion Detection for In-Vehicle Networks Using Knowledge Distillation From BERT to CNN-BiLSTM},
  journal   = {IEEE Transactions on Information Forensics and Security},
  year      = {2025},
  volume    = {20},
  pages     = {6398-6412},
  doi       = {10.1109/tifs.2025.3581117},
  url       = {https://doi.org/10.1109/tifs.2025.3581117}
}
```

---

## 2. Full Formal Abstract

> Under the development of intelligent transportation systems, In-Vehicle Networks (IVNs) serve as a critical channel for both internal and external communications. However, the inherent complexity and diversity of data traffic present significant challenges for the detection of IVN anomalous flows. Meanwhile, the introduction of various novel technologies has introduced new security vulnerabilities to IVNs. These vulnerabilities significantly impact the security of IVNs and the accuracy of in-vehicle Intrusion Detection Systems (IDS). To address these issues, this paper proposes a lightweight and efficient anomaly detection method based on knowledge distillation technology, termed Knowledge Distillation from BERT to CNN-BiLSTM (KDBC). Specifically, the KDBC distills the deep semantic knowledge from the BERT model into a more lightweight CNN-BiLSTM architecture, significantly reducing computational overhead and storage requirements without substantially compromising detection performance. Experimental results demonstrate that the KDBC model enhances both security and versatility, achieving superior detection accuracy in identifying abnormal attacks across diverse IVN data, including automotive Ethernet and CAN networks. Moreover, the KDBC model has been validated for its effectiveness and robustness in actual in-vehicle gateway environments, achieving an accuracy of over 0.98 and an F1 score greater than 0.98.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Multi-family attack flows including DoS, Fuzzy, Spoofing, and Replay.

### B. Proposed Methodology & Architecture
Pre-trains a heavy BERT model on CAN frame token sequences to learn bidirectional contextual semantics across arbitration IDs and payload bytes. Employs response-based and feature-based knowledge distillation to transfer learned representations into a compact CNN-BiLSTM student.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Survival Dataset, Real Automotive CAN Testbed

### D. Key Contributions
- First work systematically distilling bidirectional transformer attention into a compact CNN-BiLSTM for in-vehicle networks.
- Maintains 98.8% of the teacher BERT model's detection capability while reducing parameter count by 78%.
- Achieves sub-millisecond inference time on edge hardware.

### E. Quantitative Performance Metrics
- **Results:** Detection accuracy 99.42%, F1-score 0.9938, inference latency reduced by 72% vs BERT.

### F. Limitations & Research Gaps
- Requires expensive offline teacher pretraining; student CNN-BiLSTM still relies on recurrent hidden states and dense FP32 operations with non-negligible dynamic power dissipation.

### G. Direct Synergy & Comparison to SpikeBench
- Illustrates the trend of scaling down complex deep learning architectures for edge ECUs. SpikeBench provides an alternative paradigm: neuromorphic temporal coding with zero MAC operations.
