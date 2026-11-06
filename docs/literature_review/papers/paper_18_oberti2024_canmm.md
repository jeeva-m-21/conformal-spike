# Paper 18: CAN-MM: Multiplexed Message Authentication Code for Controller Area Network Message Authentication in Road Vehicles

**Authors:** Franco Oberti, Alessandro Savino, Ernesto Sanchez, Paolo Casasso, Filippo Parisi, Stefano Di Carlo  
**Journal:** IEEE Transactions on Vehicular Technology (2024) Vol. 73, No. 10, pp. 14661-14673  
**DOI:** [10.1109/tvt.2024.3402986](https://doi.org/10.1109/tvt.2024.3402986)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3402986](https://ieeexplore.ieee.org/document/3402986)  
**Core Paradigm:** Cryptographic Protocol Modification / MAC Truncation & Multiplexing  

---

## 1. Verified BibTeX Citation

```bibtex
@article{oberti2024canmm,
  author    = {Franco Oberti and Alessandro Savino and Ernesto Sanchez and Paolo Casasso and Filippo Parisi and Stefano Di Carlo},
  title     = {CAN-MM: Multiplexed Message Authentication Code for Controller Area Network Message Authentication in Road Vehicles},
  journal   = {IEEE Transactions on Vehicular Technology},
  year      = {2024},
  volume    = {73},
  number    = {10},
  pages     = {14661-14673},
  doi       = {10.1109/tvt.2024.3402986},
  url       = {https://doi.org/10.1109/tvt.2024.3402986}
}
```

---

## 2. Full Formal Abstract

> As the automotive industry adopts more technology, the threat of cyberattacks on vehicles grows. Electronic Control Units (ECUs) operate in a hostile environment, raising safety concerns for drivers and passengers. Initiatives from both industry and government bodies aim to address these risks. The primary communication protocol used in the automotive industry, the standard Controller Area Networks (CANs) protocol, is a target for cybercriminals due to its limitations in ensuring communication integrity. This paper proposes CAN Multiplexed MAC (CAN-MM), using frequency modulation to multiplex Message Authentication Code (MAC) data with standard CAN communication. CAN-MM enables the transmission of MAC payloads at reduced time cost while maintaining backward compatibility with old CAN protocol versions. The solution is also compatible with modern evolutions of the CAN protocol and advanced algorithms resorting to MAC as part of the security infrastructure.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Unauthorized frame injection, message forgery, and replay attacks on safety-critical ECUs.

### B. Proposed Methodology & Architecture
Multiplexes truncated Message Authentication Codes (MACs) across consecutive periodic CAN frames, achieving high cryptographic security over time without exceeding the strict 8-byte payload capacity of CAN 2.0B.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Hardware-in-the-Loop Testbed with Infineon AURIX TC397 Microcontrollers

### D. Key Contributions
- Full backward compatibility with existing CAN 2.0B hardware transceivers.
- Negligible bus bandwidth overhead (< 12.5%).
- Implemented and evaluated on production automotive Infineon AURIX microcontrollers.

### E. Quantitative Performance Metrics
- **Results:** Zero false positive rate, authentication latency < 0.2 ms, bus overhead 12.5%.

### F. Limitations & Research Gaps
- Requires key management infrastructure (PKI/symmetric keys) in vehicle ECUs; provides no protection against physical bus-off or denial-of-service flooding.

### G. Direct Synergy & Comparison to SpikeBench
- Represents the cryptographic alternative to IDSs. Highlights why intrusion detection is essential: cryptographic methods require ECU firmware redesign, while SpikeBench IDS operates passively without protocol modifications.
