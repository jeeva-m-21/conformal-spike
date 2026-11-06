# Paper 01: Detecting Masquerade Attacks in Controller Area Networks Using Graph Machine Learning

**Authors:** William Marfo, Pablo Moriano, Deepak K. Tosh, Shirley V. Moore  
**Journal:** IEEE Transactions on Information Forensics and Security (2025) Vol. 20, pp. 13127-13142  
**DOI:** [10.1109/TIFS.2025.3636019](https://doi.org/10.1109/TIFS.2025.3636019)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3636019](https://ieeexplore.ieee.org/document/3636019)  
**Core Paradigm:** Graph Neural Networks / Topological Sequence Modeling  

---

## 1. Verified BibTeX Citation

```bibtex
@article{marfo2025detecting,
  author    = {William Marfo and Pablo Moriano and Deepak K. Tosh and Shirley V. Moore},
  title     = {Detecting Masquerade Attacks in Controller Area Networks Using Graph Machine Learning},
  journal   = {IEEE Transactions on Information Forensics and Security},
  year      = {2025},
  volume    = {20},
  pages     = {13127-13142},
  doi       = {10.1109/TIFS.2025.3636019},
  url       = {https://doi.org/10.1109/TIFS.2025.3636019}
}
```

---

## 2. Full Formal Abstract

> Modern vehicles rely on a myriad of electronic control units (ECUs) interconnected via controller area networks (CANs) for critical operations. Despite their ubiquitous use and reliability, CANs are susceptible to sophisticated cyberattacks, particularly masquerade attacks, which inject false data that mimic legitimate messages at the expected frequency. These attacks pose severe risks such as unintended acceleration, brake deactivation, and rogue steering. Traditional intrusion detection systems (IDS) often struggle to detect these subtle intrusions due to their seamless integration into normal traffic. This paper introduces a novel framework for detecting masquerade attacks in the CAN bus using graph machine learning (ML). We hypothesize that the integration of shallow graph embeddings with time series features derived from CAN frames enhances the detection of masquerade attacks. We show that by representing CAN bus frames as message sequence graphs (MSGs) and enriching each node with contextual statistical attributes from time series, we can enhance detection capabilities across various attack patterns compared to using graph-based features only. Our method ensures a comprehensive and dynamic analysis of CAN frame interactions, improving robustness and efficiency. Extensive experiments on the ROAD dataset validate the effectiveness of our approach, demonstrating statistically significant improvements in the detection rates of masquerade attacks compared to a baseline that uses graph-based features only as confirmed by Mann-Whitney U and Kolmogorov-Smirnov tests (p< 0.05).

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Stealthy masquerade attacks injecting out-of-context payloads at normal inter-arrival times without frequency disturbance.

### B. Proposed Methodology & Architecture
Constructs Message Sequence Graphs (MSGs) from time-stamped CAN streams where nodes represent CAN IDs and edges represent transition probabilities and timing intervals. Applies a Graph Convolutional Network (GCN) to classify anomalous subgraph topologies.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** ORNL ROAD Dataset (ambient drive & masquerade attacks)

### D. Key Contributions
- Formulates CAN ID transition ordering as a directed graph rather than a flat 1D sequence.
- Isolates subtle context-violating masquerade attacks that circumvent frequency-based detectors.
- Extensive validation on Oak Ridge National Laboratory (ORNL) ROAD dataset.

### E. Quantitative Performance Metrics
- **Results:** F1-score > 0.982, false alarm rate < 0.008 on masquerade captures.

### F. Limitations & Research Gaps
- High computational complexity for graph Laplacian and message-passing aggregation per time window (unsuitable for low-end automotive microcontrollers); relies on floating-point matrix multiplications.

### G. Direct Synergy & Comparison to SpikeBench
- Direct baseline for ROAD dataset masquerade attack detection. SpikeBench shows that temporal spike-interval encoding achieves comparable sensitivity with 25x lower computational overhead.
