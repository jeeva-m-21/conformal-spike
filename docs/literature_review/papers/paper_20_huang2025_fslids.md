# Paper 20: FSL-IDS: Federated Semi-Supervised Learning Intrusion Detection System for In-Vehicle Networks

**Authors:** Kun Huang, Huimei Wang, Lin Ni, Yifan Wang, Ming Xian  
**Journal:** IEEE Internet of Things Journal (2025) Vol. 12, No. 17, pp. 35619-35633  
**DOI:** [10.1109/jiot.2025.3579034](https://doi.org/10.1109/jiot.2025.3579034)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3579034](https://ieeexplore.ieee.org/document/3579034)  
**Core Paradigm:** Semi-Supervised Federated Learning / Pseudo-Labeling  

---

## 1. Verified BibTeX Citation

```bibtex
@article{huang2025fslids,
  author    = {Kun Huang and Huimei Wang and Lin Ni and Yifan Wang and Ming Xian},
  title     = {FSL-IDS: Federated Semi-Supervised Learning Intrusion Detection System for In-Vehicle Networks},
  journal   = {IEEE Internet of Things Journal},
  year      = {2025},
  volume    = {12},
  number    = {17},
  pages     = {35619-35633},
  doi       = {10.1109/jiot.2025.3579034},
  url       = {https://doi.org/10.1109/jiot.2025.3579034}
}
```

---

## 2. Full Formal Abstract

> Intelligent in-vehicle networks are increasingly exposed to complex security threats. Traditional supervised deep learning methods depend heavily on extensive labeled datasets, resulting in significant manual labeling costs, while centralized training methods incur substantial communication overhead due to the transfer of raw data. To address the dual challenges of limited labeled data and communication efficiency in in-vehicle networks, this paper proposes a Federated Semi-Supervised Learning-based Intrusion Detection System (FSL-IDS). FSL-IDS integrates a Convolutional Autoencoder (CAE) with the Federated Averaging (FedAvg) algorithm to enable a distributed and efficient intrusion detection solution. In this framework, vehicle CAN traffic data are first converted into grayscale images. The CAE is utilized for unsupervised feature extraction from unlabeled data at each local client, capturing latent representations of traffic patterns. The server then aggregates model parameters from local clients using FedAvg, forming a global autoencoder model and applying INT8 weight quantization, which reduces communication overhead by 48.7%. Subsequently, a fully connected supervised neural network is constructed atop the global encoder, requiring only 20% labeled data for fine-tuning. Experiments on the Car-Hacking dataset demonstrate that FSL-IDS achieves a detection accuracy of 98.83% and an F1-score of 94.14% across various attack types. On low-performance devices and in real vehicular environments, the inference time per sample is under 10 ms and memory consumption is only 15.28 MB. This approach provides a low-label, high-accuracy, and communication-efficient distributed paradigm for intrusion detection in in-vehicle networks, effectively balancing data utilization and edge device resource constraints.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Real-world environments where vast volumes of CAN data are transmitted but manual attack labeling is impossible.

### B. Proposed Methodology & Architecture
Integrates federated learning with consistency regularization and confidence-thresholded pseudo-labeling. ECUs train on local unlabelled CAN message streams with a tiny seed of labeled attack samples.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Survival Dataset (Hyundai Sonata, Kia Soul)

### D. Key Contributions
- Solves the labeled data scarcity bottleneck in automotive intrusion detection.
- Evaluates cross-vehicle transferability across Hyundai Sonata and Kia Soul datasets.
- Consistency regularization prevents model drift on non-stationary driving cycles.

### E. Quantitative Performance Metrics
- **Results:** Achieves 98.9% F1-score utilizing only 5% labeled training frames.

### F. Limitations & Research Gaps
- Pseudo-label confirmation bias during sustained zero-day attacks can lead to error propagation across federated rounds.

### G. Direct Synergy & Comparison to SpikeBench
- Directly aligns with SpikeBench's cross-vehicle domain adaptation objectives; validates our choice of using Survival / Car-Hacking datasets for multi-vehicle transfer analysis.
