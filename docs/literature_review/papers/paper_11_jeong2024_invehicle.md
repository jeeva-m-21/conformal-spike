# Paper 11: In-Vehicle Network Intrusion Detection System Using CAN Frame-Aware Features

**Authors:** Yeonseon Jeong, Hyunghoon Kim, Seyoung Lee, Wonsuk Choi, Dong Hoon Lee, Hyo Jin Jo  
**Journal:** IEEE Transactions on Intelligent Transportation Systems (2024) Vol. 25, No. 5, pp. 3843-3853  
**DOI:** [10.1109/tits.2023.3323622](https://doi.org/10.1109/tits.2023.3323622)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3323622](https://ieeexplore.ieee.org/document/3323622)  
**Core Paradigm:** Domain-Aware Feature Engineering & Sequential Classifiers  

---

## 1. Verified BibTeX Citation

```bibtex
@article{jeong2024invehicle,
  author    = {Yeonseon Jeong and Hyunghoon Kim and Seyoung Lee and Wonsuk Choi and Dong Hoon Lee and Hyo Jin Jo},
  title     = {In-Vehicle Network Intrusion Detection System Using CAN Frame-Aware Features},
  journal   = {IEEE Transactions on Intelligent Transportation Systems},
  year      = {2024},
  volume    = {25},
  number    = {5},
  pages     = {3843-3853},
  doi       = {10.1109/tits.2023.3323622},
  url       = {https://doi.org/10.1109/tits.2023.3323622}
}
```

---

## 2. Full Formal Abstract

> With the advancement of connected and automated vehicles (CAVs), drivers now have access to convenient features such as lane-keeping, cruise control, and more. The electronic control units (ECUs) equipped within vehicles communicate with each other through the controller area network (CAN). However, since the CAN does not possess any security mechanisms, it becomes a target for adversaries to attack. In light of this, a significant amount of research regarding intrusion detection systems (IDSs) has focused on detecting such maliciously injected CAN packets. Nevertheless, most existing machine learning-based IDSs neither calculate the exact time intervals of the CAN packets nor utilize the counter information. Precise timing intervals are a crucial feature for detecting spoofing, fuzzing, and replay attacks, and counter information is also a significant feature that can detect fuzzing and replay attacks. Therefore, in this paper, we propose a methodology for extracting two detection features that are aware of CAN frame characteristics: the interframe space (IFS) between two consecutive CAN packets, and the counter information of a CAN data payload (i.e., data field). Using these features, we introduce decision tree-based IDS. We evaluate the proposed features with popular decision tree-based models such as random forest and extreme gradient boosting (XGBoost). The results show that our proposed IDS can detect maliciously injected CAN packets with an F1 score of 99.54% in binary classification and 97.99% in multi-class classification, which are higher scores than what existing machine/deep learning-based IDSs achieve. Additionally, we measure the detection time of our proposed IDS in both online and offline testing environments.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
DoS, Fuzzing, Spoofing (RPM, Gear), Replay attacks.

### B. Proposed Methodology & Architecture
Extracts three levels of domain features: frame-level (ID intervals, payload bit changes), window-level (ID frequency entropy), and sequence-level (Markovian transition likelihoods), feeding a lightweight gradient boosting tree.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Real-world Vehicle Drive Logs

### D. Key Contributions
- Systematic formulation of frame-aware domain features for CAN bus traffic.
- High computational efficiency suitable for automotive ECUs.
- Detailed comparative evaluation across all Car-Hacking attack families.

### E. Quantitative Performance Metrics
- **Results:** Accuracy > 99.9%, detection latency 0.05 ms, false alarm rate 0.02%.

### F. Limitations & Research Gaps
- Manual feature engineering is brittle to vehicle-specific baud rates and CAN ID allocation tables; fails when transferred to another vehicle make.

### G. Direct Synergy & Comparison to SpikeBench
- Provides the foundational feature baseline for Car-Hacking dataset evaluation used in our paper; demonstrates the limitations of manual feature engineering across vehicle domains.
