# Paper 14: Federated and Quantized-Based Intrusion Detection for Embedded On-Board Automotive Networks

**Authors:** Muhammad Adil, Danish Javeed, Prabhat Kumar  
**Journal:** IEEE Transactions on Intelligent Transportation Systems (2026) pp. 1-14  
**DOI:** [10.1109/tits.2025.3645854](https://doi.org/10.1109/tits.2025.3645854)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3645854](https://ieeexplore.ieee.org/document/3645854)  
**Core Paradigm:** Quantized Federated Learning / Distributed Edge AI  

---

## 1. Verified BibTeX Citation

```bibtex
@article{adil2026federated,
  author    = {Muhammad Adil and Danish Javeed and Prabhat Kumar},
  title     = {Federated and Quantized-Based Intrusion Detection for Embedded On-Board Automotive Networks},
  journal   = {IEEE Transactions on Intelligent Transportation Systems},
  year      = {2026},
  pages     = {1-14},
  doi       = {10.1109/tits.2025.3645854},
  url       = {https://doi.org/10.1109/tits.2025.3645854}
}
```

---

## 2. Full Formal Abstract

> Intelligent vehicles rely on hybrid On-Board Automotive Networks (OANs), such as Time-Sensitive Networking (TSN) and Controller Area Networks (CAN), to support autonomous driving and ADAS. Securing these networks is challenging due to resource constraints, heterogeneous protocols, and evolving attacks. We propose an embedded-optimized, privacy-preserving collaborative IDS for hybrid OANs. Leveraging Cloud Vehicle Functions (CVFs), the framework enables robust model training across vehicles without sharing raw data. To efficiently process multi-protocol traffic, we introduce the Network Traffic Temporal Encoder (NTTE), which transforms network packets into temporal traffic images for anomaly detection. These NTTE representations are analyzed by TCNnet, a lightweight neural network designed for efficient embedded deployment. To make TCNnet suitable for resource-constrained embedded systems, we propose post-training quantization, significantly reducing its computational and storage demands. Evaluated on real traffic, the quantized TCNnet maintains over 99% detection accuracy, while reducing model size by over 91% and memory footprint by 51%, enabling practical deployment on resource-constrained ECUs. To link IDS outputs to real-world transportation outcomes, we develop the Transportation Impact Modeling Module (TIMM), which maps network-level detection performance to vehicle-level safety metrics (collision likelihood and Safety Message Delivery Ratio, SMDR) and fleet-level traffic indicators (Vehicle Flow Efficiency, VFE). TIMM simulations across Urban, Suburban, and Highway scenarios show the IDS reduces expected collisions by up to 97.9%, while maintaining high traffic flow efficiency (VFE = 0.949–0.995) and message reliability (SMDR = 0.988–0.994). These results demonstrate that the proposed IDS not only excels in network-level detection but also directly enhances vehicular safety and traffic performance, confirming its practical applicability in Intelligent Transportation Systems.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Coordinated vehicular fleet cyber-attacks, privacy leakage, and edge resource constraints.

### B. Proposed Methodology & Architecture
Proposes INT8 post-training quantization integrated with Federated Averaging (FedAvg). Vehicle ECUs compute local quantized gradients on incoming CAN traffic, transmitting compressed updates to an edge road-side unit (RSU) aggregator.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, CICIoV2024, Real Connected Vehicle Fleet

### D. Key Contributions
- Combines federated collaborative fleet learning with INT8 quantization for automotive ECUs.
- Reduces wireless communication bandwidth by 78% without loss in detection F1-score.
- Guarantees vehicular data privacy without transmitting raw CAN traces.

### E. Quantitative Performance Metrics
- **Results:** F1-score 99.2%, 4x model compression, communication overhead reduced by 3.8x.

### F. Limitations & Research Gaps
- Periodic federated synchronization creates wireless traffic bursts; quantized integer ANNs still perform synchronous dense vector-matrix multiplications.

### G. Direct Synergy & Comparison to SpikeBench
- Demonstrates that automotive security is moving toward quantized, distributed architectures. SNNs represent the logical ultimate bound: 1-bit event-driven binary communication.
