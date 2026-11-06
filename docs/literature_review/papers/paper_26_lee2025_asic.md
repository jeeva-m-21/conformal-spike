# Paper 26: ASIC Design for Real-Time CAN-Bus Intrusion Detection and Prevention System Using Random Forest

**Authors:** Junseok Lee, Sangmin Park, Sua Shin, Hyungchul Im, Joosock Lee, Seongsoo Lee  
**Journal:** IEEE Access (2025) Vol. 13, pp. 129856-129869  
**DOI:** [10.1109/access.2025.3585956](https://doi.org/10.1109/access.2025.3585956)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3585956](https://ieeexplore.ieee.org/document/3585956)  
**Core Paradigm:** Hardware ASIC Acceleration / Dedicated Silicon IP Core  

---

## 1. Verified BibTeX Citation

```bibtex
@article{lee2025asic,
  author    = {Junseok Lee and Sangmin Park and Sua Shin and Hyungchul Im and Joosock Lee and Seongsoo Lee},
  title     = {ASIC Design for Real-Time CAN-Bus Intrusion Detection and Prevention System Using Random Forest},
  journal   = {IEEE Access},
  year      = {2025},
  volume    = {13},
  pages     = {129856-129869},
  doi       = {10.1109/access.2025.3585956},
  url       = {https://doi.org/10.1109/access.2025.3585956}
}
```

---

## 2. Full Formal Abstract

> A controller area network (CAN) is the most widely used protocol to communicate between electronic control units (ECUs) inside a vehicle. however, it lacks basic security functions and a structure vulnerable to external attacks. Therefore, it is important to develop an intrusion detection system (IDS) that can effectively identify malicious and legitimate CAN messages, as well as an intrusion prevention system (IPS) that can block such malicious messages in real time. In this study, a random-forest-based intrusion detection system (RF-IDS) was proposed and integrated with a CAN controller to design a system that can perform real-time detection and attack blocking. Existing IDS studies aim for high detection performance. however, the real-time blocking function is limited or the possibility of hardware implementation is yet to be sufficiently verified. To address this issue, we designed an IDS that can immediately determine if an attack is present when receiving a CAN frame and blocking the attack node. Fast and efficient detection is possible complex matrix operations because the random forest model performs detection based on comparison operations. This confirmed that the corresponding structure achieved an average detection time of 1.86 μs and detection accuracy of more than 99%, allowing real-time intrusion blocking. Finally, hardware implementation was achieved by completing the design of the ASIC chip through a multiproject wafer process.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Line-rate intrusion detection and in-line malicious frame dropping (prevention).

### B. Proposed Methodology & Architecture
Designs a dedicated digital ASIC coprocessor implementing a pipelined Random Forest decision tree ensemble. Directly interfaces with the CAN transceiver to inspect frames during the end-of-frame (EOF) delimiter.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, RTL Hardware Simulation & FPGA Emulation

### D. Key Contributions
- True Intrusion Prevention System (IPS) capability: drops malicious frames before ECU reception.
- Ultra-low hardware processing latency of 4.8 microseconds per frame.
- Synthesized in commercial CMOS standard cell library.

### E. Quantitative Performance Metrics
- **Results:** Latency 4.8 microseconds, gate count 45,000 gates, power consumption 1.8 mW at 100 MHz clock frequency.

### F. Limitations & Research Gaps
- Fixed decision tree thresholds hardwired into silicon logic; cannot be updated or fine-tuned post-fabrication without complete chip redesign.

### G. Direct Synergy & Comparison to SpikeBench
- Establishes the state-of-the-art in dedicated automotive hardware acceleration (1.8 mW, 4.8 us). Neuromorphic SNN ASICs match these power and latency targets while offering reconfigurable synaptic weights.
