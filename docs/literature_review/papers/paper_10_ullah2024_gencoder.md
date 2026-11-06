# Paper 10: GenCoder: A Generative AI-Based Adaptive Intra-Vehicle Intrusion Detection System

**Authors:** Mikhail Smolin  
**Journal:** IEEE Access (2024) Vol. 12, pp. 150651-150663  
**DOI:** [10.1109/access.2024.3476177](https://doi.org/10.1109/access.2024.3476177)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3476177](https://ieeexplore.ieee.org/document/3476177)  
**Core Paradigm:** Generative Deep Learning / Autoencoder Anomaly Detection  

---

## 1. Verified BibTeX Citation

```bibtex
@article{ullah2024gencoder,
  author    = {Mikhail Smolin},
  title     = {GenCoder: A Generative AI-Based Adaptive Intra-Vehicle Intrusion Detection System},
  journal   = {IEEE Access},
  year      = {2024},
  volume    = {12},
  pages     = {150651-150663},
  doi       = {10.1109/access.2024.3476177},
  url       = {https://doi.org/10.1109/access.2024.3476177}
}
```

---

## 2. Full Formal Abstract

> With the rapid expansion of the vehicular cybersecurity (VCS) market and the increasing sophistication of cyberthreats, developing an adaptive intra-vehicular intrusion detection system (IDS) is crucial. This paper introduces GenCoder, a generative artificial intelligence (GenAI)-based IDS that uniquely addresses the dynamic and evolving nature of vehicular cyberthreats. GenCoder combines a five-layer deep neural network (DNN) with a variational autoencoder (VAE), overseen by a novel communication layer known as the GenCoder layer. This system dynamically adapts to new intrusion patterns by generating and utilizing new training data when deviations from known patterns are detected. The generated samples have a Shannon entropy (SE) value of 1.65 bits for four classes, indicating standard variety among the synthetic data. GenCoder demonstrates exceptional adaptability, pushing the accuracy, precision, recall, and F1-score from 84.79%, 83.58%, 83.70%, and 83.64% to 92.19%, 90.12%, 90.44%, and 90.28%, respectively, after introducing 50% feature deformation to testing data. The novel concept of an adaptive intra-vehicular IDS, the innovative GenCoder layer that establishes seamless communication among the DNN, the VAE, and the dataset, as well as the unique assessment strategies of adaptability make this research exceptional with the potential to create a new dimension in automotive IDS research.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Zero-day injection attacks, masquerade attacks, and unseen manipulation patterns.

### B. Proposed Methodology & Architecture
Unsupervised deep autoencoder architecture trained exclusively on benign CAN message transitions. During inference, injected attack frames produce elevated reconstruction error vectors that deviate from nominal manifold projections.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** Car-Hacking Dataset, SynCAN Dataset

### D. Key Contributions
- Eliminates the need for labeled attack data during training.
- Robust reconstruction scoring resilient to minor traffic noise.
- Extensive testing across synthetic and physical CAN datasets.

### E. Quantitative Performance Metrics
- **Results:** Detection accuracy 99.78%, precision 99.82%, AUC-ROC 0.9991.

### F. Limitations & Research Gaps
- Autoencoders require continuous floating-point matrix multiplications for encoder-decoder passes, demanding substantial GPU/TPU compute on edge ECUs.

### G. Direct Synergy & Comparison to SpikeBench
- Exemplifies unsupervised autoencoding on CAN bus. SpikeBench replaces continuous floating-point reconstruction with membrane potential thresholding in spiking autoencoders.
