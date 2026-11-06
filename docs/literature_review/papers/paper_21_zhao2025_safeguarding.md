# Paper 21: Safeguarding GRU-Based Intrusion Detection Systems From Adversarial Attacks With Dynamic Label Watermark in CAN Bus Communication

**Authors:** Haihang Zhao, Yi Wang, Anyu Cheng, Shanshan Wang, Jing Yuan, Hongrong Wang  
**Journal:** IEEE Internet of Things Journal (2025) Vol. 12, No. 7, pp. 7668-7676  
**DOI:** [10.1109/jiot.2024.3524504](https://doi.org/10.1109/jiot.2024.3524504)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3524504](https://ieeexplore.ieee.org/document/3524504)  
**Core Paradigm:** Adversarial Defense / Dynamic Payload Watermarking  

---

## 1. Verified BibTeX Citation

```bibtex
@article{zhao2025safeguarding,
  author    = {Haihang Zhao and Yi Wang and Anyu Cheng and Shanshan Wang and Jing Yuan and Hongrong Wang},
  title     = {Safeguarding GRU-Based Intrusion Detection Systems From Adversarial Attacks With Dynamic Label Watermark in CAN Bus Communication},
  journal   = {IEEE Internet of Things Journal},
  year      = {2025},
  volume    = {12},
  number    = {7},
  pages     = {7668-7676},
  doi       = {10.1109/jiot.2024.3524504},
  url       = {https://doi.org/10.1109/jiot.2024.3524504}
}
```

---

## 2. Full Formal Abstract

> Intrusion detection systems (IDS) for control area network (CAN) bus communication using deep learning models face threats from adversarial closed-box. attacks in the Internet of Vehicles (IoVs). Although watermark techniques are proposed as defences, they lack concealment and are vulnerable. Current watermark methods for time-series data-based applications need cloud-based verification and terminal-based generation, and they cannot meet real-time requirements with large resources. To address these issues, we propose a real-time gated recurrent units (GRUs) based IDS with for CAN bus communication via a novel dynamic label watermark (DLW) method. In detail, we design a multitask learning structure at the terminal side only to detect conventional intrusion attacks. At the same time, we propose a novel DLW method applied to time-series data to defend against adversarial closed-box. attacks. Experimental results show that for the detection of Denial of Service (DoS), revolutions per minute (RPM) spoofing, and fuzzing attacks, our model achieves 1.00000, 1.00000, and close to 1.00000 with the recall, accuracy, F1 score, and precision, respectively. For detection of gear spoofing, our model with the same metrics achieves 1.00000, which are 0.0882, 0.0001, 0.0459, and 0.0208 better than CANLite and the same as ConvLSTM-GNB. Finally, we construct a new adversarial closed-box. attack embedded with four attacks above to validate the resistance and performance of our model (achieving 116 KB code size), which is 58% smaller, 0.9%–35.7% faster, and 1.52%–10.5% improvement of same metrics compared to the baseline model (LSTM).

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Adversarial evasion attacks where subtle bit perturbations in non-critical CAN payload bytes deceive deep neural networks.

### B. Proposed Methodology & Architecture
Embeds dynamic pseudo-random cryptographic watermarks into designated reserved payload bits during transmission. The receiving IDS verifies watermark integrity before recurrent GRU feature extraction, neutralizing adversarial perturbations.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Adversarial Perturbation Benchmarks (FGSM, PGD, CW)

### D. Key Contributions
- Identifies the acute vulnerability of RNN/GRU automotive IDSs to adversarial evasion.
- Lightweight dynamic watermark generation without noticeable payload overhead.
- Restores high detection accuracy under white-box and black-box gradient attacks.

### E. Quantitative Performance Metrics
- **Results:** Restores F1-score from 0.42 to 0.984 under PGD adversarial attacks; watermark verification latency < 0.02 ms.

### F. Limitations & Research Gaps
- Requires sender ECU modification to inject watermarks; ineffective if the attacker gains bus-mastering control.

### G. Direct Synergy & Comparison to SpikeBench
- CRITICAL INSIGHT FOR SNNs: Demonstrates that continuous deep networks (like GRUs) are brittle to adversarial evasion. Spiking neural networks naturally resist gradient-based evasion due to non-differentiable spiking thresholds.
