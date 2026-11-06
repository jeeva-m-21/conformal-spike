# Paper 06: Lightweight and Adaptive Data-Driven Intrusion Detection System for Autonomous Vehicles

**Authors:** Wael Aljabri, Md. Abdul Hamid, Rayan Mosli  
**Journal:** IEEE Transactions on Intelligent Transportation Systems (2025) Vol. 26, No. 2, pp. 2282-2292  
**DOI:** [10.1109/tits.2024.3509459](https://doi.org/10.1109/tits.2024.3509459)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3509459](https://ieeexplore.ieee.org/document/3509459)  
**Core Paradigm:** Adaptive Ensemble Machine Learning / Dual-Domain IDS  

---

## 1. Verified BibTeX Citation

```bibtex
@article{aljabri2025lightweight,
  author    = {Wael Aljabri and Md. Abdul Hamid and Rayan Mosli},
  title     = {Lightweight and Adaptive Data-Driven Intrusion Detection System for Autonomous Vehicles},
  journal   = {IEEE Transactions on Intelligent Transportation Systems},
  year      = {2025},
  volume    = {26},
  number    = {2},
  pages     = {2282-2292},
  doi       = {10.1109/tits.2024.3509459},
  url       = {https://doi.org/10.1109/tits.2024.3509459}
}
```

---

## 2. Full Formal Abstract

> Autonomous vehicles are equipped with numerous electronic control units (ECUs). These ECUs are interconnected via in-vehicle networks to ensure safety, assist drivers, and perform various functions. A controller area network (CAN) facilitates real-time data transmission between ECUs. CAN provides sufficient reliability for communication within vehicles. Modern vehicles also utilize vehicle-to-everything (V2X) technologies. V2X enables vehicles to link to external networks, facilitating communication with other vehicles, infrastructures, and electronic devices. Modern vehicles’ enhanced functionality and connections make them more susceptible to cyberattacks on both in-vehicle and external networks because of their extensive attack surfaces. To address this issue, this research presents a novel data-driven intrusion detection system (IDS) designed for in-vehicle and external communication networks. The proposed IDS can effectively detect many types of intrusions beyond the constraints of binary classifications. This system underwent a comprehensive evaluation using three in-vehicle datasets: car-hacking, car-hacking: attack & defense Challenge, and the ROAD datasets. Additionally, it was evaluated on two external communication network datasets: CICIDS2017 and CSE-CIC-IDS2018. The evaluation results demonstrated the IDS’s adaptability, achieving significant accuracy, recall, and F1 scores. It attained up to 99.99% accuracy with the in-vehicle datasets. Moreover, it exhibited an exceptionally low false-positive rate, as low as 0, in the Car-Hacking dataset. The proposed IDS architecture is a lightweight approach compared to state-of-the-art models. It significantly reduced complexity in terms of Floating-Point Operations per Second (FLOPs), memory usage, and learning parameters, all without compromising performance.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Unified threat model spanning internal CAN bus intrusions and external V2X communication attacks.

### B. Proposed Methodology & Architecture
Employs automated feature selection (mutual information and recursive feature elimination) coupled with an adaptive ensemble classifier to handle both in-vehicle bus data and external IP network packets.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking, Car-Hacking Challenge, ORNL ROAD Dataset, CICIDS2017/2018

### D. Key Contributions
- One of the few studies simultaneously evaluated on Car-Hacking, Car-Hacking Challenge, and ROAD datasets.
- Dual-domain coverage protecting both internal ECUs and external V2X gateways.
- Exceptionally low false positive rate (< 0.01%).

### E. Quantitative Performance Metrics
- **Results:** Accuracy up to 99.99% on in-vehicle datasets, F1-score > 0.999.

### F. Limitations & Research Gaps
- Does not investigate cross-vehicle transferability; models trained on Car-Hacking are not evaluated zero-shot on ROAD without retraining.

### G. Direct Synergy & Comparison to SpikeBench
- Provides a comprehensive baseline across the exact three benchmarks analyzed in our work (Car-Hacking, Challenge, ROAD). SpikeBench builds upon this by exploring cross-vehicle domain shifts.
