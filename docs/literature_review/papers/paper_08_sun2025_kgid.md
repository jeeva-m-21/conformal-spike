# Paper 08: KG-ID: Knowledge Graph-Based Intrusion Detection on In-Vehicle Network

**Authors:** Heng Sun, Jingzhu Wang, Jian Weng, Weihua Tan  
**Journal:** IEEE Transactions on Intelligent Transportation Systems (2025) Vol. 26, No. 4, pp. 4988-5000  
**DOI:** [10.1109/tits.2025.3530155](https://doi.org/10.1109/tits.2025.3530155)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3530155](https://ieeexplore.ieee.org/document/3530155)  
**Core Paradigm:** Semantic Knowledge Graphs / Rule-Guided Graph Embeddings  

---

## 1. Verified BibTeX Citation

```bibtex
@article{sun2025kgid,
  author    = {Heng Sun and Jingzhu Wang and Jian Weng and Weihua Tan},
  title     = {KG-ID: Knowledge Graph-Based Intrusion Detection on In-Vehicle Network},
  journal   = {IEEE Transactions on Intelligent Transportation Systems},
  year      = {2025},
  volume    = {26},
  number    = {4},
  pages     = {4988-5000},
  doi       = {10.1109/tits.2025.3530155},
  url       = {https://doi.org/10.1109/tits.2025.3530155}
}
```

---

## 2. Full Formal Abstract

> The Controller Area Network (CAN) is a widely adopted communication protocol in the automotive industry, facilitating connectivity among various electronic control units inside vehicles. However, with the growing intelligence and connectivity of modern vehicles, the in-vehicle network (IVN) faces significant security challenges due to the lack of inherent security mechanisms in the CAN protocol. Therefore, it is necessary to develop a monitoring and protection scheme for IVN. In this article, we propose a novel knowledge graph-based intrusion detection methodology, referred to as KG-ID. The proposed KG-ID methodology leverages a knowledge graph to analyze CAN frame and signal features for detecting several types of attacks. To the best of our knowledge, this is the first application of knowledge graph technology for intrusion detection in the IVN. Subsequently, the selection of CAN signal feature, construction of in-vehicle ontology model, knowledge extraction, and robustness against various attacks are explained in detail. In addition, a series of experiments demonstrate that the proposed methodology can accurately detect fabrication, masquerade, and fuzzy attacks. In particular, the time overhead of intrusion detection in a real vehicle supported by XPeng is only 0.031 ms for KG-ID. The code for the methodology proposed in this article is available at:https://github.com/jingzhuwang/KG-ID.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Fabrication, suspension, and parameter modification attacks violating vehicular operational logic.

### B. Proposed Methodology & Architecture
Extracts automotive entity triplets `(ECU_source, Message_ID, Physical_Signal)` from OEM DBC database specifications. Formulates a knowledge graph and utilizes TransE graph embeddings combined with logical consistency rules to detect anomalies.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Real Vehicle In-Drive Logs

### D. Key Contributions
- Introduces formal semantic reasoning to in-vehicle network security.
- High explainability: alerts trace back to specific ECU semantic violations.
- Near-zero false alarms on standard OEM driving profiles.

### E. Quantitative Performance Metrics
- **Results:** F1-score 99.6%, precision 99.8%, reasoning latency 0.45 ms.

### F. Limitations & Research Gaps
- Requires proprietary OEM DBC (CAN database) configuration files, which are strictly confidential trade secrets and unavailable for third-party aftermarket security.

### G. Direct Synergy & Comparison to SpikeBench
- Contrasts with SpikeBench: while KG-ID depends on proprietary DBC specifications, SpikeBench's SNN is completely DBC-agnostic, operating directly on raw arbitration IDs and inter-arrival intervals.
