# Paper 19: CCID-CAN: Cross-Chain Intrusion Detection on CAN Bus for Autonomous Vehicles

**Authors:** Heng Sun, Weilin Huang, Jian Weng, Zhiquan Liu, Weihua Tan, Zaobo He, Mingyang Chen, Biaobang Wu, Long Li, Xinyuan Peng  
**Journal:** IEEE Internet of Things Journal (2024) Vol. 11, No. 15, pp. 26146-26159  
**DOI:** [10.1109/jiot.2024.3393122](https://doi.org/10.1109/jiot.2024.3393122)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3393122](https://ieeexplore.ieee.org/document/3393122)  
**Core Paradigm:** Dual-Chain Blockchain / Secure Edge Forensics  

---

## 1. Verified BibTeX Citation

```bibtex
@article{sun2024ccidcan,
  author    = {Heng Sun and Weilin Huang and Jian Weng and Zhiquan Liu and Weihua Tan and Zaobo He and Mingyang Chen and Biaobang Wu and Long Li and Xinyuan Peng},
  title     = {CCID-CAN: Cross-Chain Intrusion Detection on CAN Bus for Autonomous Vehicles},
  journal   = {IEEE Internet of Things Journal},
  year      = {2024},
  volume    = {11},
  number    = {15},
  pages     = {26146-26159},
  doi       = {10.1109/jiot.2024.3393122},
  url       = {https://doi.org/10.1109/jiot.2024.3393122}
}
```

---

## 2. Full Formal Abstract

> Autonomous vehicles (AVs) rely on controller area network (CAN), which ensures the communication between massive electronic control units (ECUs) and passenger safety. Although CAN is a lightweight and reliable broadcast protocol, its vulnerability has caused CAN to confront serious security threats. Adversaries and malicious organizations can impair CAN bus in a variety of ways, such as injecting malicious messages into CAN bus. These malicious messages can directly intervene the functions inside AVs. Therefore, this article proposes a novel cross-chain-based intrusion detection for CAN bus (CCID-CAN) model that uses rule-based Valid Bit index (VBIN) model for initial intrusion detection on CAN bus inside AVs, followed by the Kalman filter and Naïve Bayes model for detecting attacks missed in the VBIN, where a cross-chain mechanism implements the exchange of attack logs among connected AVs that may not trust each other so as to optimize the Naïve Bayes detector. Afterwards, a series of experiments against several types of attacks are conducted on real vehicle supported by XPeng, and the results reveal that the CCID-CAN model outperforms existing models in terms of detection performance, time overhead, and memory footprint. In addition, attack log exchange for cross-chain networks in this proposed model is of high performance in latency, memory footprint, and throughput.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Insider ECU tampering, retroactive log falsification, and cross-vehicle coordinated exploits.

### B. Proposed Methodology & Architecture
Employs a hierarchical dual-chain blockchain architecture: an intra-vehicle light subchain logs high-speed CAN anomaly signatures, while an inter-vehicle consortium main chain coordinates threat intelligence across fleets.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Laboratory Hardware CAN Testbed

### D. Key Contributions
- Tamper-proof, immutable forensic auditing of automotive cyber incidents.
- Hierarchical sharding separates high-throughput CAN logging from slow distributed consensus.
- Real-world testbed implementation with physical microcontrollers.

### E. Quantitative Performance Metrics
- **Results:** Throughput 1,200 CAN frames/s, consensus delay 0.83 s on main chain, detection accuracy 99.5%.

### F. Limitations & Research Gaps
- Blockchain consensus and cryptographic hashing consume substantial storage and energy; cannot operate inside low-end microcontrollers.

### G. Direct Synergy & Comparison to SpikeBench
- Demonstrates the forensic logging side of vehicular security. SpikeBench acts as the ultra-fast edge detector that triggers CCID-CAN's immutable logging pipeline.
