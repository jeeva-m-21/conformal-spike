# Paper 17: DCANFL: Decentralized Federated Learning for In-Vehicle CAN Intrusion Detection

**Authors:** Yunjian Jia, Zirui Liu, Wanli Wen, Tian Tian, Liang Liang  
**Journal:** IEEE Transactions on Vehicular Technology (2026) Vol. 75, No. 8, pp. 18397-18402  
**DOI:** [10.1109/tvt.2026.3671351](https://doi.org/10.1109/tvt.2026.3671351)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3671351](https://ieeexplore.ieee.org/document/3671351)  
**Core Paradigm:** Decentralized Blockchain Federated Learning / Peer-to-Peer Consensus  

---

## 1. Verified BibTeX Citation

```bibtex
@article{jia2026dcanfl,
  author    = {Yunjian Jia and Zirui Liu and Wanli Wen and Tian Tian and Liang Liang},
  title     = {DCANFL: Decentralized Federated Learning for In-Vehicle CAN Intrusion Detection},
  journal   = {IEEE Transactions on Vehicular Technology},
  year      = {2026},
  volume    = {75},
  number    = {8},
  pages     = {18397-18402},
  doi       = {10.1109/tvt.2026.3671351},
  url       = {https://doi.org/10.1109/tvt.2026.3671351}
}
```

---

## 2. Full Formal Abstract

> The controller area network (CAN) bus, a core in-vehicle communication protocol, is highly vulnerable to cyber attacks due to its lack of built-in security mechanisms. While many intrusion detection systems (IDS) have been proposed, most rely on centralized training that requires sensitive data to be uploaded to a server, raising privacy and deployment concerns. Federated learning (FL) mitigates these issues by keeping data local, yet conventional FL still depends on a central coordinator, making it unsuitable for vehicular networks with intermittent connectivity and single points of failure. To address these challenges, we propose DCANFL, a decentralized FL framework for in-vehicle CAN intrusion detection. DCANFL uses gossip-based, dissimilarity-driven pairing for efficient model exchange and a continual learning training pipeline to improve performance and maintain high accuracy across diverse attack types. Experiments on two in-vehicle CAN datasets show that DCANFL, without central server coordination, achieves better detection performance than centralized FedAvg and other decentralized FL baselines.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Central server failure, model poisoning attacks, and coordinated automotive botnets.

### B. Proposed Methodology & Architecture
Replaces central server aggregation with a peer-to-peer decentralized federated learning scheme among vehicular gateway nodes. Incorporates a reputation-weighted consensus algorithm to filter poisoned local model updates.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, ORNL ROAD Dataset

### D. Key Contributions
- Eliminates single points of failure in centralized vehicular federated learning.
- Tolerates up to 30% Byzantine malicious vehicular participants.
- Dual validation on Car-Hacking and the realistic ROAD dataset.

### E. Quantitative Performance Metrics
- **Results:** F1-score 98.7% under 20% poisoning adversary presence; convergence speed improved by 25%.

### F. Limitations & Research Gaps
- Consensus mechanism introduces additional communication overhead across inter-vehicle V2V links.

### G. Direct Synergy & Comparison to SpikeBench
- Bridges federated learning with real-world ROAD evaluation; demonstrates how decentralized edge models can collaborate across vehicle fleets.
