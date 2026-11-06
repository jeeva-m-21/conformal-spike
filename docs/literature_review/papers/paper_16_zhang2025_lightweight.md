# Paper 16: A Lightweight Voltage-Based ECU Fingerprint Intrusion Detection System for In-Vehicle CAN Bus

**Authors:** Man Zhang, Jini Li, Yu Lai, Sha Huan, Wenli Shang  
**Journal:** IEEE Transactions on Vehicular Technology (2025) Vol. 74, No. 10, pp. 15536-15548  
**DOI:** [10.1109/tvt.2025.3570961](https://doi.org/10.1109/tvt.2025.3570961)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3570961](https://ieeexplore.ieee.org/document/3570961)  
**Core Paradigm:** Physical-Layer Fingerprinting / Analog Signal Analytics  

---

## 1. Verified BibTeX Citation

```bibtex
@article{zhang2025lightweight,
  author    = {Man Zhang and Jini Li and Yu Lai and Sha Huan and Wenli Shang},
  title     = {A Lightweight Voltage-Based ECU Fingerprint Intrusion Detection System for In-Vehicle CAN Bus},
  journal   = {IEEE Transactions on Vehicular Technology},
  year      = {2025},
  volume    = {74},
  number    = {10},
  pages     = {15536-15548},
  doi       = {10.1109/tvt.2025.3570961},
  url       = {https://doi.org/10.1109/tvt.2025.3570961}
}
```

---

## 2. Full Formal Abstract

> The Controller Area Network (CAN) is the de facto industry standard of In-Vehicle Network (IVN) for connecting Electronic Control Units (ECUs). In recent years, related researchers have proposed various in-vehicle network security schemes to protect CAN bus. By leveraging the physical characteristics of signals sent by ECUs, ECU identification methods are proposed to implement intrusion detection system at the physical transmission layer. Voltage-based physical fingerprint techniques have gained significant attention in this research field. Considering the resource-constrained embedded environments of IVN, various methods attempt to reduce the resource requirements of physical fingerprint-based ECU identification methods. In this paper, a lightweight voltage-based fingerprint intrusion detection system is proposed, which achieves an identification accuracy of over 99% under conditions of low sampling rates, short signal segments, and a small feature set through comprehensive experiments on both CAN prototypes and a rich dataset of ten actual vehicles.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Transmitter masquerade attacks where an adversary ECU injects frames using the arbitration ID of a legitimate ECU.

### B. Proposed Methodology & Architecture
Captures analog differential voltage waveforms (CAN_H - CAN_L) during frame arbitration. Extracts lightweight statistical voltage features (rising edge slope, plateau variance, ringing frequency) using low-sampling-rate ADCs.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** 10 Real Production Vehicles (Toyota, Honda, Volkswagen, Ford, etc.)

### D. Key Contributions
- Operates at relatively low sampling rates (5–10 MS/s), substantially lower than oscilloscope-based methods (1 GS/s).
- Evaluated across 10 actual production vehicles from diverse automotive brands.
- Provides physical-layer authentication that cannot be spoofed by software injection.

### E. Quantitative Performance Metrics
- **Results:** ECU identification accuracy > 99.1%, processing time 0.18 ms/frame.

### F. Limitations & Research Gaps
- Requires dedicated analog-to-digital hardware tapped into physical CAN wiring; sensitive to wiring age, temperature variations, and battery voltage fluctuation.

### G. Direct Synergy & Comparison to SpikeBench
- Complements cyber-domain IDSs. While physical fingerprinting requires custom hardware sensors, SpikeBench operates directly on the digital protocol layer accessible via standard CAN transceivers.
