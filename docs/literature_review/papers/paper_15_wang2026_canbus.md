# Paper 15: CAN Bus Intrusion Detection Based on Deep Learning With Data Augmentation for Connected Autonomous Vehicles

**Authors:** Xiang Wang, Jian Zhao, Pengbo Liu, Nianmin Yao, Zheng Xu  
**Journal:** IEEE Transactions on Vehicular Technology (2026) Vol. 75, No. 2, pp. 2253-2266  
**DOI:** [10.1109/tvt.2025.3603056](https://doi.org/10.1109/tvt.2025.3603056)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3603056](https://ieeexplore.ieee.org/document/3603056)  
**Core Paradigm:** Generative Data Augmentation / Residual CNN-LSTM  

---

## 1. Verified BibTeX Citation

```bibtex
@article{wang2026canbus,
  author    = {Xiang Wang and Jian Zhao and Pengbo Liu and Nianmin Yao and Zheng Xu},
  title     = {CAN Bus Intrusion Detection Based on Deep Learning With Data Augmentation for Connected Autonomous Vehicles},
  journal   = {IEEE Transactions on Vehicular Technology},
  year      = {2026},
  volume    = {75},
  number    = {2},
  pages     = {2253-2266},
  doi       = {10.1109/tvt.2025.3603056},
  url       = {https://doi.org/10.1109/tvt.2025.3603056}
}
```

---

## 2. Full Formal Abstract

> As the de-facto standard for in-vehicle networks, the Controller Area Network (CAN) is exposed to different types of cyber-attacks due to the lack of security mechanisms. Intrusion Detection Systems (IDS) can be deployed to identify the attacks by monitoring host and network activities. However, there is little abnormal historical data that can be used to train deep learning models, resulting in data imbalance and biased trained model. Hence, we propose a prediction-based IDS framework for detecting the attacks on a CAN bus, which consists of two deeplearning models of the data augmentation module and the prediction module. Firstly, the Generative Adversarial Networks (GAN) was utilized as the data augmentation module to automatically generate high-quality attack data and balance the training set. Two networks were introduced as the prediction module, and the first one is a convolutional neural networks (CNN) that predicts correlated data of all CAN IDs, and the second one is an LSTM that predicts messages individually using times series data for each CAN ID. Furthermore, an intrusion detection equipment for the CAN bus was designed and the real vehicle test was conducted. The experimental results show that the proposed method can detect CAN attacks, with an average F1-score of 99.74% and an accuracy of 99.78%. Compared with the reference work, the F1-score of attack detection is improved by 15.25%, and also the detection time is reduced by 29.11%.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Imbalanced attack injection where anomalous frames represent < 1% of total traffic.

### B. Proposed Methodology & Architecture
Combines Conditional Generative Adversarial Networks (CGAN) and adaptive SMOTE to synthesize high-fidelity minority attack samples. The augmented balance is used to train a residual CNN-LSTM architecture.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, Simulated High-Noise Automotive Testbed

### D. Key Contributions
- Resolves severe class imbalance in automotive CAN attack benchmarks.
- Residual CNN-LSTM architecture effectively captures both spatial bit relations and temporal recurrence.
- Demonstrates high stability in low-frequency injection scenarios.

### E. Quantitative Performance Metrics
- **Results:** Average F1-score 99.74%, accuracy 99.78%, false negative rate reduced by 84%.

### F. Limitations & Research Gaps
- Generative sample synthesis can generate out-of-distribution artifacts not representative of real physical ECU state transitions.

### G. Direct Synergy & Comparison to SpikeBench
- Directly addresses the severe class imbalance problem that caused constant SNN metrics in our initial transfer tests. Confirms the necessity of threshold calibration and AUPRC metrics.
