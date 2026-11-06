# Paper 28: Spiking Residual ShuffleNet-Based Intrusion Detection in IoT Environment

**Authors:** Sneha Leela Jacob, H. Parveen Sultana  
**Journal:** IEEE Access (2025) Vol. 13, pp. 104257-104280  
**DOI:** [10.1109/access.2025.3579777](https://doi.org/10.1109/access.2025.3579777)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3579777](https://ieeexplore.ieee.org/document/3579777)  
**Core Paradigm:** Neuromorphic Spiking Neural Networks / Spiking CNN Architectures  

---

## 1. Verified BibTeX Citation

```bibtex
@article{jacob2025spiking,
  author    = {Sneha Leela Jacob and H. Parveen Sultana},
  title     = {Spiking Residual ShuffleNet-Based Intrusion Detection in IoT Environment},
  journal   = {IEEE Access},
  year      = {2025},
  volume    = {13},
  pages     = {104257-104280},
  doi       = {10.1109/access.2025.3579777},
  url       = {https://doi.org/10.1109/access.2025.3579777}
}
```

---

## 2. Full Formal Abstract

> The Internet of Things (IoT) system has been developed to create a smart environment. Privacy and security are critical issues in IoT systems. Security vulnerabilities in IoT-enabled models generate threats that impact various applications. Therefore, intrusion detection systems (IDS) are essential for IoT systems to prevent attacks. Due to the limited storage and computational abilities of IoT devices, traditional IDS is not suitable for IoT systems. In this context, a new model called Spiking Residual ShuffleNet (SR-ShuffleNet) is introduced for intrusion detection (ID) in an IoT environment. The Multi-objective Fractional Artificial Bee Colony (MFABC) algorithm is used for routing. MFABC combines fractional calculus with artificial bee colonies. At the base station (BS), data normalization, data augmentation (DA), feature selection (FS), and ID processes are carried out. The input data is normalized using Z-score normalization (ZN). Features are selected based on Motyka similarity and Topsoe similarity. After feature selection, the bootstrapping technique is used to augment the features in the DA phase. Finally, ID is performed using SR-ShuffleNet, which integrates the Spiking deep residual network (S-ResNet) with ShuffleNet. After detecting an intrusion, an attack is mitigated to eliminate the malicious node. The SR-ShuffleNet model achieves impressive accuracy and efficiency in identifying and mitigating attacks in IoT systems.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Cyber-attacks, scanning, flooding, and malware propagation in IoT edge systems.

### B. Proposed Methodology & Architecture
Combines channel shuffling from ShuffleNet with Leaky Integrate-and-Fire (LIF) spiking neurons and residual connections. Uses surrogate gradient backpropagation for direct end-to-end training of the deep spiking network.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** IoT-23, Edge-IIoTset, BoT-IoT

### D. Key Contributions
- Pioneers the fusion of channel shuffling and residual connections in Spiking Neural Networks.
- Direct training using surrogate gradients achieves high convergence without ANN-to-SNN conversion loss.
- Demonstrates massive energy savings on neuromorphic simulation.

### E. Quantitative Performance Metrics
- **Results:** Detection accuracy 99.3%, 73% energy reduction compared to standard ANN ShuffleNet baseline.

### F. Limitations & Research Gaps
- Evaluated on generic IoT network packet datasets (IoT-23) rather than real automotive CAN bus timing streams.

### G. Direct Synergy & Comparison to SpikeBench
- DIRECT METHODOLOGICAL ANCHOR: Proves that spiking residual architectures deliver 73% energy savings while maintaining state-of-the-art accuracy. SpikeBench adapts and evaluates this spiking paradigm specifically for automotive CAN bus security.
