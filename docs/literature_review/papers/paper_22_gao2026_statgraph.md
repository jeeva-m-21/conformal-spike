# Paper 22: StatGraph: Effective In-Vehicle Intrusion Detection via Multi-View Statistical Graph Learning

**Authors:** Kai Wang, Qiguang Jiang, Bailing Wang, Yulei Wu, Hongke Zhang  
**Journal:** IEEE Transactions on Mobile Computing (2026) Vol. 25, No. 5, pp. 6335-6351  
**DOI:** [10.1109/tmc.2025.3636517](https://doi.org/10.1109/tmc.2025.3636517)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3636517](https://ieeexplore.ieee.org/document/3636517)  
**Core Paradigm:** Multi-View Graph Convolutional Networks (GCN)  

---

## 1. Verified BibTeX Citation

```bibtex
@article{gao2026statgraph,
  author    = {Kai Wang and Qiguang Jiang and Bailing Wang and Yulei Wu and Hongke Zhang},
  title     = {StatGraph: Effective In-Vehicle Intrusion Detection via Multi-View Statistical Graph Learning},
  journal   = {IEEE Transactions on Mobile Computing},
  year      = {2026},
  volume    = {25},
  number    = {5},
  pages     = {6335-6351},
  doi       = {10.1109/tmc.2025.3636517},
  url       = {https://doi.org/10.1109/tmc.2025.3636517}
}
```

---

## 2. Full Formal Abstract

> In-vehicle networks (IVNs) face growing threats from advanced cyber-attacks, particularly stealthy masquerade attacks that mimic legitimate message patterns. This paper proposes STATGRAPH, a fine-grained intrusion detection frame work based on multi-view statistical graph learning over the Controller Area Network (CAN) messages within IVNs. STAT GRAPH constructs two graphs per detection window: a Timing Correlation Graph (TCG) capturing temporal ID dependencies, and a Coupling Relationship Graph (CRG) modeling short term contextual relations. TCG and CRG are further used to generate graph structure encoding payload variations and embedded signal co-occurrence. A lightweight multi-layered Graph Convolutional Network (GCN) is then applied to classify each message, leveraging the expressive representations from TCG and CRG. To ensure effectiveness against diverse attacks, we evaluate STATGRAPH on two real-world CAN datasets featuring five underexplored masquerade attacks. Experimental results show that STATGRAPH significantly improves detection granularity and outperforms state-of-the-art methods, with F1-score gains of 7% and 22%, while maintaining the highest accuracy. Code is available at https://github.com/wangkai-tech23/StatGraph

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Stealthy masquerade attacks and multi-ECU coordinated spoofing.

### B. Proposed Methodology & Architecture
Constructs two complementary graphs per sliding detection window: a Timing Correlation Graph (TCG) capturing inter-ID temporal transition statistics, and a Coupling Relationship Graph (CRG) modeling payload covariance. A multi-layer GCN performs joint node classification.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, ORNL ROAD Dataset

### D. Key Contributions
- Multi-view graph formulation capturing both timing dynamics and payload semantics.
- Demonstrates superior performance on the ORNL ROAD dataset against subtle masquerade attacks.
- Outperforms single-view graph models and classical sequence baselines.

### E. Quantitative Performance Metrics
- **Results:** F1-score 99.4% on ROAD masquerade attacks; average detection delay 1.2 ms.

### F. Limitations & Research Gaps
- Constructing two dynamic graphs per window entails substantial matrix construction and message-passing overhead, exceeding the compute budget of standard ECUs.

### G. Direct Synergy & Comparison to SpikeBench
- State-of-the-art graph ML baseline on the ROAD dataset. SpikeBench achieves comparable masquerade sensitivity while operating directly on event spikes with > 80% lower arithmetic operations.
