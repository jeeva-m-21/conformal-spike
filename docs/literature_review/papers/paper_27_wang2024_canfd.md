# Paper 27: Intrusion Detection System for In-Vehicle CAN-FD Bus ID Based on GAN Model

**Authors:** Xu Wang, Yihu Xu, Yinan Xu, Ziyi Wang, Yujing Wu  
**Journal:** IEEE Access (2024) Vol. 12, pp. 82402-82412  
**DOI:** [10.1109/access.2024.3412933](https://doi.org/10.1109/access.2024.3412933)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3412933](https://ieeexplore.ieee.org/document/3412933)  
**Core Paradigm:** Generative Adversarial Networks (GAN) / Next-Gen Protocol IDS  

---

## 1. Verified BibTeX Citation

```bibtex
@article{wang2024canfd,
  author    = {Xu Wang and Yihu Xu and Yinan Xu and Ziyi Wang and Yujing Wu},
  title     = {Intrusion Detection System for In-Vehicle CAN-FD Bus ID Based on GAN Model},
  journal   = {IEEE Access},
  year      = {2024},
  volume    = {12},
  pages     = {82402-82412},
  doi       = {10.1109/access.2024.3412933},
  url       = {https://doi.org/10.1109/access.2024.3412933}
}
```

---

## 2. Full Formal Abstract

> The growing abundance of electronic control units and peripheral devices loaded and connected to smart connected cars has resulted in a constant stream of cyber-attacks at various levels and dimensions. The CAN-FD bus plays a crucial role in smart connected cars. Currently, the majority of research efforts remain centered around the traditional CAN bus, with fewer studies addressing intrusion detection for the CAN-FD bus in smart connected vehicles. CAN-FD boasts a notable improvement in transmission speed, capable of reaching up to 8 Mbps compared to the 1 Mbps of the standard CAN bus. Utilizing intrusion detection systems designed for the CAN bus in high-speed CAN-FD applications could potentially hinder normal transmission and detection efficiency. Hence, we focus on the attack and intrusion detection of CAN-FD bus ID nodes to prevent unauthorized access and potential malicious attacks. We propose an ID intrusion detection system based on an improved Generative Adversarial Network (GAN) model, which consists of two parts: a data pre-processing module and a detection module. To apply the GAN model to the vehicle bus, we perform pre-processing of the bus data. We introduce the concept of dual discriminator to improve the detection rate and enable the handling of unknown attacks. With the output of dual discriminator, we can determine whether there are any anomalies in the detection data. First, we use a data pre-processing module to convert the ID segments of the automobile CAN-FD into binary image encoding to form ID images. Subsequently, these ID images are fed into an ID image feature extractor in the detection module to extract various auxiliary features. The discriminator receives these auxiliary features and calculates the probability of whether the received image is a normal ID image or not to determine the authenticity of the ID image. The experimental results show that the proposed intrusion detection system is able to detect a message within 0.15 ms, which fully meets the real-time detection requirements while the vehicle is in motion. The average detection rate of the proposed system for different types of attacks is 99.93%, which is an average of 1.2% improvement of the detection rate over the GIDS algorithm. The proposed system not only ensures the normal communication of CAN-FD bus but also realizes real-time and accurate intrusion detection.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
High-bandwidth, high-payload (up to 64 bytes) injection attacks on CAN-FD networks.

### B. Proposed Methodology & Architecture
Focuses on the CAN with Flexible Data-rate (CAN-FD) protocol. Implements a conditional GAN to model high-throughput frame arrival distributions and payload dynamics at 5 Mbps bitrates.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** CAN-FD Physical Hardware Rig, Synthetic Injection Logs

### D. Key Contributions
- One of the first comprehensive deep learning IDSs specifically tailored for CAN-FD.
- Handles up to 64 bytes of payload per frame (8x larger than classical CAN).
- Sub-millisecond detection compliant with high-speed autonomous driving buses.

### E. Quantitative Performance Metrics
- **Results:** Detection latency 0.15 ms, accuracy 99.8% on 64-byte high-speed CAN-FD traffic.

### F. Limitations & Research Gaps
- High GAN training instability and mode collapse on complex multi-ECU high-payload variations.

### G. Direct Synergy & Comparison to SpikeBench
- Demonstrates that next-generation vehicular systems demand scalable IDSs capable of handling expanded payloads and higher bitrates. SNN event-driven sparse computation scales efficiently with increased bandwidth.
