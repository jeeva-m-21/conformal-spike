# Paper 05: T-Shaped CAN Feature Integration With Lightweight Deep Learning Model for In-Vehicle Network Intrusion Detection

**Authors:** Sha Huan, Xiaoyi Zhang, Wenli Shang, Haitao Cao, Heng Li, Yuanjia Yang, Wenbai Liu  
**Journal:** IEEE Transactions on Intelligent Transportation Systems (2024) Vol. 25, No. 12, pp. 21183-21196  
**DOI:** [10.1109/tits.2024.3478371](https://doi.org/10.1109/tits.2024.3478371)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3478371](https://ieeexplore.ieee.org/document/3478371)  
**Core Paradigm:** Spatio-Temporal Feature Fusion / Depthwise Separable CNN-GRU  

---

## 1. Verified BibTeX Citation

```bibtex
@article{huan2024tshaped,
  author    = {Sha Huan and Xiaoyi Zhang and Wenli Shang and Haitao Cao and Heng Li and Yuanjia Yang and Wenbai Liu},
  title     = {T-Shaped CAN Feature Integration With Lightweight Deep Learning Model for In-Vehicle Network Intrusion Detection},
  journal   = {IEEE Transactions on Intelligent Transportation Systems},
  year      = {2024},
  volume    = {25},
  number    = {12},
  pages     = {21183-21196},
  doi       = {10.1109/tits.2024.3478371},
  url       = {https://doi.org/10.1109/tits.2024.3478371}
}
```

---

## 2. Full Formal Abstract

> With the continuous advancement of automotive intelligence and ubiquitous connection, In-Vehicle Networks (IVN) are confronted with heightened security challenges. Attackers can inject false messages to manipulate or disrupt critical functional modules on the vehicle, leading to significant safety issues. Given the real-time requirements and resource constraints of the in-vehicle network, a lightweight Intrusion Detection System (IDS) is needed to deal with the security threats caused by attacks. This paper proposes an effective intrusion detection method to address these requirements. The method combines refined CAN traffic features with a lightweight Deep Learning (DL) network. The time interval series, ID and the CAN message payload are extracted by a T-shaped window, vectorized to form a one-dimensional data frame, and the detection is completed by a lightweight 1D deep learning model using efficient convolution calculation. In binary and multiclass experiments on two publicly available datasets, the feature refinement strategy is discussed. Compared to existing deep learning-based intrusion detection methods, our approach demonstrates advantages in both intrusion detection performance and computational complexity, highlighting its deployment potential in embedded IVN environments.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
DoS, Fuzzy, Gear Spoofing, RPM Spoofing.

### B. Proposed Methodology & Architecture
Constructs a "T-shaped" feature matrix integrating intra-frame structure (ID bits, DLC, CRC, payload bytes) with inter-frame temporal sequence intervals. The matrix is classified by a lightweight depthwise separable CNN coupled with a gated recurrent unit (GRU).

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset and Real Vehicle Road-Test Logs

### D. Key Contributions
- Novel T-shaped spatial-temporal representation linking frame metadata and sequential transitions.
- Depthwise separable convolutions minimize FLOPs for microcontroller deployment.
- Extensive real-vehicle road test verification.

### E. Quantitative Performance Metrics
- **Results:** Detection accuracy 99.85%, F1-score 0.9982, inference time 0.12 ms/window.

### F. Limitations & Research Gaps
- Fixed sliding window size (e.g. 64 frames) introduces detection lag; dense GRU matrix operations consume continuous clock cycles even when the bus is idle.

### G. Direct Synergy & Comparison to SpikeBench
- Reinforces the value of combining spatial message structure with inter-arrival intervals; SpikeBench embeds both dimensions into 2D temporal spike trains.
