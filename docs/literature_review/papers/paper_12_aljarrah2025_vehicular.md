# Paper 12: Vehicular Intrusion Detection System for Controller Area Network: A Comprehensive Survey and Evaluation

**Authors:** Yangyang Liu, Lei Xue, Sishan Wang, Xiapu Luo, Kaifa Zhao, Pengfei Jing, Xiaobo Ma, Yajuan Tang, Haiying Zhou  
**Journal:** IEEE Transactions on Intelligent Transportation Systems (2025) Vol. 26, No. 7, pp. 10979-11009  
**DOI:** [10.1109/tits.2025.3567940](https://doi.org/10.1109/tits.2025.3567940)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3567940](https://ieeexplore.ieee.org/document/3567940)  
**Core Paradigm:** Systematic Survey, Taxonomy, and Empirical Benchmarking  

---

## 1. Verified BibTeX Citation

```bibtex
@article{aljarrah2025vehicular,
  author    = {Yangyang Liu and Lei Xue and Sishan Wang and Xiapu Luo and Kaifa Zhao and Pengfei Jing and Xiaobo Ma and Yajuan Tang and Haiying Zhou},
  title     = {Vehicular Intrusion Detection System for Controller Area Network: A Comprehensive Survey and Evaluation},
  journal   = {IEEE Transactions on Intelligent Transportation Systems},
  year      = {2025},
  volume    = {26},
  number    = {7},
  pages     = {10979-11009},
  doi       = {10.1109/tits.2025.3567940},
  url       = {https://doi.org/10.1109/tits.2025.3567940}
}
```

---

## 2. Full Formal Abstract

> The progress of automotive technologies has made cybersecurity a crucial focus, leading to various cyber attacks. These attacks primarily target the Controller Area Network (CAN) and specialized Electronic Control Units (ECUs). In order to mitigate these attacks and bolster the security of vehicular systems, numerous defense solutions have been proposed. These solutions aim to detect diverse forms of vehicular attacks. However, the practical implementation of these solutions still presents certain limitations and challenges. In light of these circumstances, this paper undertakes a thorough examination of existing vehicular attacks and defense strategies employed against the CAN and ECUs. The objective is to provide valuable insights and inform the future design of Vehicular Intrusion Detection Systems (VIDS). The findings of our investigation reveal that the examined VIDS primarily concentrate on particular categories of attacks, neglecting the broader spectrum of potential threats. Moreover, we provide a comprehensive overview of the significant challenges encountered in implementing a robust and feasible VIDS. Additionally, we put forth several defense recommendations based on our study findings, aiming to inform and guide the future design of VIDS in the context of vehicular security.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Comprehensive taxonomy covering fabrication, suspension, masquerade, and physical-layer attacks.

### B. Proposed Methodology & Architecture
Synthesizes over 150 CAN IDS publications (2018–2025), taxonomizes methods into rule-based, physical-fingerprint, machine learning, and deep learning, and re-implements 12 representative detectors under unified evaluation metrics.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking, ROAD, Survival, TU-Dortmund, SynCAN

### D. Key Contributions
- Definitive reference survey on Controller Area Network intrusion detection.
- Identifies the "Evaluation Crisis" in CAN security: models reporting > 99% accuracy on Car-Hacking fail catastrophically on ROAD.
- Calls for standardized cross-vehicle transferability and energy accounting.

### E. Quantitative Performance Metrics
- **Results:** Comprehensive cross-benchmark evaluation showing severe performance drop (> 40% F1 decrease) when testing cross-dataset.

### F. Limitations & Research Gaps
- Survey paper; does not propose a new neuromorphic architecture.

### G. Direct Synergy & Comparison to SpikeBench
- CRITICAL BENCHMARKING ANCHOR: Highlights the exact problem SpikeBench solves—unmasking the synthetic ease of Car-Hacking and addressing the cross-vehicle domain gap on real-world datasets like ROAD.
