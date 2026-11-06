# Paper 29: A Neuromorphic Approach to DDoS Detection: Hardware Accelerator for Integer-Quantized Spiking Neural Networks

**Authors:** Phu Nguyen Phan Hai, Khang Pham Lo Hoang, Cam Doan Ngoc, Bao Bui Quoc, Trang Hoang  
**Journal:** IEEE Access (2026) Vol. 14, pp. 81824-81839  
**DOI:** [10.1109/access.2026.3694606](https://doi.org/10.1109/access.2026.3694606)  
**IEEE Xplore:** [https://ieeexplore.ieee.org/document/3694606](https://ieeexplore.ieee.org/document/3694606)  
**Core Paradigm:** FPGA Neuromorphic Accelerator / Integer-Quantized SNN Inference  

---

## 1. Verified BibTeX Citation

```bibtex
@article{hai2026neuromorphic,
  author    = {Phu Nguyen Phan Hai and Khang Pham Lo Hoang and Cam Doan Ngoc and Bao Bui Quoc and Trang Hoang},
  title     = {A Neuromorphic Approach to DDoS Detection: Hardware Accelerator for Integer-Quantized Spiking Neural Networks},
  journal   = {IEEE Access},
  year      = {2026},
  volume    = {14},
  pages     = {81824-81839},
  doi       = {10.1109/access.2026.3694606},
  url       = {https://doi.org/10.1109/access.2026.3694606}
}
```

---

## 2. Full Formal Abstract

> Distributed Denial of Service (DDoS) attacks remain a persistent threat to Internet of Things (IoT) and edge networks, where detection systems are often constrained by latency and power budgets. This paper presents a SNN based DDoS detection system that spans packet level preprocessing, integer quantized inference, and FPGA deployment. A learnable leaky integrate and fire (LIF) input encoder with per feature firing thresholds is introduced to transform normalized traffic features into spike trains in a trainable manner. The entire inference pipeline operates in integer arithmetic through quantization aware training, eliminating all floating point operations. A four stage pipelined hardware accelerator is implemented on a Xilinx Zynq UltraScale+ multiprocessor system-on-chip (MPSoC). Experiments on the Bot IoT and ToN IoT datasets demonstrate competitive detection accuracy, and the accelerator achieves an inference latency of 91.58 μs, delivering a 182.1× speedup over the ARM Cortex A53 with 10.95% FPGA logic utilization.

---

## 3. In-Depth Technical Summary

### A. Threat Model & Problem Formulation
Volumetric flooding, high-rate denial of service, and packet amplification attacks.

### B. Proposed Methodology & Architecture
Designs an FPGA-based hardware accelerator executing integer-quantized Spiking Neural Networks. Employs packet-level event encoding where packet headers directly trigger spike generation, processed through integer addition pipelines with zero floating-point operations.

### C. Datasets & Experimental Benchmark
- **Datasets Evaluated:** CICDDoS2019, CAIDA Dataset

### D. Key Contributions
- Purely integer-based neuromorphic hardware pipeline eliminating all floating-point multipliers.
- Line-rate packet processing capable of handling 10 Gbps network interfaces.
- Demonstrates real-time hardware execution on low-cost Xilinx Artix-7 FPGA.

### E. Quantitative Performance Metrics
- **Results:** Line-rate throughput at 10 Gbps, 1.4 W total power on Artix-7 FPGA, F1-score 99.6%.

### F. Limitations & Research Gaps
- Fixed integer bit-width quantization can saturate under sudden bursty noise unless dynamic threshold scaling is incorporated.

### G. Direct Synergy & Comparison to SpikeBench
- VALIDATES SPIKEBENCH SYNAPTIC ACCOUNTING: Proves that neuromorphic SNN inference is completely MAC-free, requiring only integer additions upon spike arrival. This directly supports our theoretical power model for automotive CAN flooding defense.
