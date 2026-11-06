# Paper 03: CANLP: Intrusion Detection for Controller Area Networks Using Natural Language Processing and Embedded Machine Learning

**Authors:** Kavya Balasubramanian, Adithya Gowda Baragur, Denis Donadel, Dinuka Sahabandu, Alessandro Brighente, Bhaskar Ramasubramanian, Mauro Conti, Radha Poovendran  
**Journal:** IEEE Transactions on Dependable and Secure Computing (2025) Vol. 22, No. 6, pp. 7203-7214  
**DOI:** [10.1109/tdsc.2025.3596516](https://doi.org/10.1109/tdsc.2025.3596516)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3596516](https://ieeexplore.ieee.org/document/3596516)  
**Core Paradigm:** Natural Language Processing / N-gram Tokenization  

---

## 1. Verified BibTeX Citation

```bibtex
@article{balasubramanian2025canlp,
  author    = {Kavya Balasubramanian and Adithya Gowda Baragur and Denis Donadel and Dinuka Sahabandu and Alessandro Brighente and Bhaskar Ramasubramanian and Mauro Conti and Radha Poovendran},
  title     = {CANLP: Intrusion Detection for Controller Area Networks Using Natural Language Processing and Embedded Machine Learning},
  journal   = {IEEE Transactions on Dependable and Secure Computing},
  year      = {2025},
  volume    = {22},
  number    = {6},
  pages     = {7203-7214},
  doi       = {10.1109/tdsc.2025.3596516},
  url       = {https://doi.org/10.1109/tdsc.2025.3596516}
}
```

---

## 2. Full Formal Abstract

> The Controller Area Network (CAN) protocol is the most widely used standard in the automotive industry for in-vehicle networks. However, the CAN protocol lacks essential security features such as encryption and message authentication. Absence of such security features has been shown to make the vehicle network vulnerable to exploits by an adversary. Although multiple types of intrusion detection systems (IDS) have been developed for CAN, it can be difficult to deploy them in real-time with low latency. Further, many of these IDSs are unable to isolate specific CAN frames on which an attack has been mounted, which makes it challenging to design defense mechanisms. In this paper, we develop CANLP, a Natural Language Processing (NLP)-based intrusion detection system to determine whether each transmitted message originated from a legitimate ECU or an adversary. CANLP uses Term Frequency-Inverse Document Frequency (TF-IDF), a NLP technique to discern complex features associated with CAN data and trains machine learning models to identify three types of attacks- fuzzing, spoofing, and masquerade. When an attack is detected, CANLP identifies the malicious CAN frame, which is important for developing resilient systems. Extensive experiments on 4 publicly available vehicle network datasets (which represent data collected from over three vehicle makes and four models) show that CANLP performs attack classification with high F1-scores of 0.9974. We also show that CANLP can be deployed for attack detection on resource-constrained hardware through implementation using RaspberryPi and experiments on a testbed with latency as low as$\lt \text{0.05}~ms$, making it suitable for real-world automotive applications such as fleet monitoring within the same vehicle class.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Fuzzing, Spoofing, and Masquerade attacks across multi-vehicle platforms.

### B. Proposed Methodology & Architecture
Treats raw CAN message payload hexadecimals as words in a document. Applies Term Frequency-Inverse Document Frequency (TF-IDF) feature weighting over n-grams, followed by embedded tree ensembles to classify and isolate specific malicious frames.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** 4 Publicly Available Vehicle Datasets (3 vehicle makes, 4 models)

### D. Key Contributions
- Proposes per-frame attack attribution using NLP n-gram tokenization.
- Multi-vehicle validation across four different vehicular models.
- Lightweight tree-based inference suitable for resource-constrained microcontrollers.

### E. Quantitative Performance Metrics
- **Results:** F1-score 0.9974, sub-millisecond per-frame classification.

### F. Limitations & Research Gaps
- High memory overhead for maintaining large n-gram dictionaries and sparse TF-IDF matrices; susceptible to payload obfuscation.

### G. Direct Synergy & Comparison to SpikeBench
- Highlights the challenge of per-frame isolation across different automotive platforms. SpikeBench achieves frame-level temporal attribution using leaky integrate-and-fire spike timing.
