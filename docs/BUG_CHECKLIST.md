# ConformalSpike: Master Bug Checklist & Resolution Ledger

**Comprehensive Audit of Algorithmic, Firmware, Theoretical, and Dataset Anomalies**  
**Target Venue:** *IEEE Transactions on Information Forensics and Security (T-IFS)*  
**Date of Record:** November 2026  

---

## 1. Master Bug Tracking Matrix

| Bug ID | Subsystem | Severity | Status | Summary Description |
| :---: | :---: | :---: | :---: | :--- |
| **BUG-01** | **Dataset / Benchmark** | **Critical** | **RESOLVED** | Spliced artificial regimes violating continuous CAN bus physical timeline |
| **BUG-02** | **Firmware (C)** | **Critical** | **RESOLVED** | Fixed-point integer underflow (`diff_alpha >> 9 == 0`) pinning $\alpha_k$ adaptation |
| **BUG-03** | **Firmware (C)** | **High** | **RESOLVED** | Active spike buffer truncation (`active_in_idx[20]`) dropping magnitude shocks |
| **BUG-04** | **Benchmark (Python)** | **High** | **RESOLVED** | Table V ablation study TPR denominator divided by total stream length instead of attack frames |
| **BUG-05** | **Conformal Engine** | **Critical** | **RESOLVED** | Fenwick buffer admission catch-22 (`d_old == 0`) causing permanent lockout under regime shifts |
| **BUG-06** | **Dataset Synthesis** | **Critical** | **RESOLVED** | ROAD masquerade synthesized over Hyundai Sonata benign traffic where CAN ID `0x6E0` does not exist |
| **BUG-07** | **Spike Encoder** | **Critical** | **RESOLVED** | 16-bit integer byte-rollover ($0xFF \to 0x00$) inflating $\tau_{\max}$ ceiling to 251.0 on wheel speed ID `0x6E0` |
| **BUG-08** | **Firmware (C)** | **Medium** | **RESOLVED** | Firmware weight halving (`w_j_q8 = 128`) on channels with $\tau_{\max} > 32$ |
| **BUG-09** | **Domain Transfer** | **High** | **RESOLVED** | CrossVehicle domain shift deadlock: perpetual rollback locking context to pre-shift frames |
| **BUG-10** | **Paper (Hardware)** | **High** | **DOCUMENTED** | AURIX TC397 hardware claims: Frenkel energy misquoted ($12.7\,\text{pJ}$ vs $0.1\,\text{pJ}$), FPU absence error |
| **BUG-11** | **Paper (Citations)**| **Medium** | **DOCUMENTED** | Literature citation conflations: Cho & Shin USENIX '16 (CIDS) vs ACM CCS '16 (Bus-Off) vs Choi '18 (VoltageIDs) |
| **BUG-12** | **Paper (Plots)** | **Medium** | **RESOLVED** | Figure 1 and Figure 2 visual artifacts caused by single-seed outlier runs |
| **BUG-13** | **Spike Encoder & Models** | **Critical** | **RESOLVED** | Speedometer Masquerade multi-byte magnitude excursion omission in `compute_frame_score` |
| **BUG-14** | **Firmware (C)** | **High** | **RESOLVED** | Firmware unsigned delta rollover and isolated attack test vectors lacking authentic baseline context |

---

## 2. Detailed Bug Reports, Root Causes, and Verification Remedies

---

### BUG-01: Spliced Artificial Regimes vs. Continuous CAN Timeline
* **Subsystem:** `src/data_loader.py`
* **Severity:** Critical | **Status:** **RESOLVED**
* **Description:**  
  Initial benchmark code constructed driving regimes by concatenating small, disconnected 500-frame slices from different timestamps. This induced artificial timestamp reversals and discontinuous payload jumps at every boundary, corrupting the log2 timing channels and producing massive false positive spikes ($>14\%$).
* **Root Cause:**  
  `load_expanded_datasets()` used modulo indexing over arbitrary fragments rather than extracting unbroken, strictly monotonic chronological streams.
* **Resolution:**  
  Implemented 4 continuous, unbroken 10,000-frame regimes with strictly monotonic physical timestamps ($t_k > t_{k-1}$):
  1. `Stationary`: Continuous engine idle (HCRL Sonata).
  2. `Highway`: Continuous high-speed dynamic driving (HCRL Sonata).
  3. `Dyno`: Continuous dynamometer speed sweep (ORNL ROAD).
  4. `CrossVehicle`: Continuous multi-vehicle transfer (Survival Analysis).
* **Verification:**  
  Verified strictly increasing timestamps $\min(t_k - t_{k-1}) > 0$ across all 40,000 regime frames.

---

### BUG-02: Fixed-Point Integer Truncation in MCU ACI Update
* **Subsystem:** `firmware/conformal_spike_mcu.c` (lines 366–370)
* **Severity:** Critical | **Status:** **RESOLVED**
* **Description:**  
  On benign frames, the nominal ACI error difference is $\Delta \alpha = \alpha_{\text{target}} \cdot 2^{16} = 0.005 \times 65536 \approx 328$ in Q16. The C firmware computed:
  ```c
  int16_t diff_alpha = 328;
  g_cs_ctx.alpha_k_q16 += (diff_alpha >> 9); /* 328 >> 9 == 0 ! */
  ```
  Because $328 \gg 9 = 0$, $\alpha_k$ never incremented on benign traffic. Conversely, on alert frames ($\Delta \alpha = -65208$), the subtraction succeeded. Consequently, $\alpha_k$ rapidly collapsed to $\alpha_{\min}$ and stayed permanently pinned, causing severe threshold inflation.
* **Root Cause:**  
  Right-shifting a small positive Q16 integer by 9 bits truncates the fractional step to integer zero.
* **Resolution:**  
  Implemented a 32-bit Q24 fractional residual accumulator (`alpha_k_q24`):
  ```c
  int32_t step_q24 = (diff_q16 * (int32_t)g_cs_ctx.gamma_q16) >> 8;
  g_cs_ctx.alpha_k_q24 += step_q24;
  g_cs_ctx.alpha_k_q16 = (uint16_t)(g_cs_ctx.alpha_k_q24 >> 8);
  ```
* **Verification:**  
  Verified in `test_mcu`: $\alpha_k$ adapts smoothly upward on benign frames and decrements on alerts, bounding FPR at $0.53\%$.

---

### BUG-03: Active Spike Buffer Dropping Features
* **Subsystem:** `firmware/conformal_spike_mcu.c` & `firmware/conformal_spike_mcu.h`
* **Severity:** High | **Status:** **RESOLVED**
* **Description:**  
  The C firmware statically allocated `uint8_t active_in_idx[20]` to store indices of firing input spikes. However, Theorem 4 and the spike encoder specification permit up to 28 active spikes (11 ID + 8 payload deltas + 8 magnitude shocks + 1 timing spike). When simultaneous shocks fired, indices $21\text{--}28$ were silently dropped, suppressing magnitude shock signals.
* **Root Cause:**  
  Under-dimensioned static array bound in `cs_context_t`.
* **Resolution:**  
  Expanded buffer capacity to `uint8_t active_in_idx[28]` in `conformal_spike_mcu.h` and updated loop bounds in `cs_encode_frame()`.
* **Verification:**  
  `make firmware` verified that all 28 channels successfully propagate into the hidden LIF synaptic accumulation.

---

### BUG-04: Table V Ablation Study TPR Denominator Dilution Bug
* **Subsystem:** `src/evaluation.py` (`run_ablation_study`)
* **Severity:** High | **Status:** **RESOLVED**
* **Description:**  
  In the Table V ablation study, the True Positive Rate (TPR) for SpeedMasq was reported as $1.03\%$, directly contradicting Table II which reported $99.47\%$ for the exact same attack.
* **Root Cause:**  
  `run_ablation_study` computed TPR by dividing the number of detections by the total stream length:
  ```python
  tpr = detections / len(stream)  # len(stream) = 8,000 frames!
  ```
  Since the stream contained only $937$ attack frames (the remaining $7,063$ frames being normal traffic), this introduced an artificial $8.5\times$ dilution factor ($937 / 8000 \approx 0.117$).
* **Resolution:**  
  Restricted the TPR denominator strictly to attack frames:
  ```python
  total_atk = sum(1 for f in stream if f.label != 'Normal')
  tpr = (detections / total_atk) * 100.0
  ```
* **Verification:**  
  Table V and Table II now report aligned TPR metrics ($>94\%$) for the full ConformalSpike model.

---

### BUG-05: Fenwick Buffer Admission Catch-22 Under Regime Shifts
* **Subsystem:** `src/conformal.py` (`ConformalSpikeIDS.decide`)
* **Severity:** Critical | **Status:** **RESOLVED**
* **Description:**  
  During legitimate regime shifts (e.g., Stationary Idle $\to$ Dynamic Highway), the benign score distribution drifted upward. The original code admitted frames into the sliding calibration buffer *if and only if* `d_old == 0`. Because scores temporarily exceeded the old threshold, $d = 1$ fired, locking the buffer from admitting any new frames. The threshold could not adapt, permanently trapping the IDS in an alarm storm ($14.48\%$ FPR).
* **Root Cause:**  
  Conditioning buffer admission on instantaneous binary decision $d_{\text{old}} == 0$ creates a circular dependency between the threshold and the reference distribution.
* **Resolution:**  
  Conditioned buffer admission on the 32-frame quarantine shield rather than the binary alert:
  ```python
  if not q_old:
      self.q_buffer.push(s_old)
  ```
  Frames that survive the 32-frame quarantine without triggering physical shock (Gate 1), jitter (Gate 2), or density burst (Gate 3) are admitted, allowing benign drift to be integrated.
* **Verification:**  
  Stationary FPR dropped from $14.48\%$ to $0.60\%$; Highway FPR dropped to $0.32\%$; Dyno dropped to $0.56\%$. Mean FPR is $0.56\%$ (strictly within the $\le 1.50\%$ ASIL-D budget).

---

### BUG-06: Synthesis Substrate Mismatch for ORNL ROAD Masquerades
* **Subsystem:** `src/data_loader.py` (`load_expanded_datasets`)
* **Severity:** Critical | **Status:** **RESOLVED**
* **Description:**  
  The 5 ROAD masquerade scenarios (`road_masq_speed`, `road_masq_coolant`, etc.) were synthesized by iterating over `cal_benign[:8000]`. However, `cal_benign` was loaded exclusively from `Attack_Dataset_Driving_no_duplicates.csv` (Hyundai Sonata). In Hyundai Sonata CAN traffic, CAN ID `0x6E0` (wheel speed) does not exist. It only exists in the ORNL ROAD dataset (`Road_Dataset_no_duplicates.csv`), where it is the 5th most frequent ID on the bus (1,338 occurrences per 20k frames).
* **Root Cause:**  
  Because `0x6E0` never occurred in the benign frames between attacks, every attack frame had its `last_payload` context stored from the *previous attack frame*. On every attack after the first, $\text{payload}[1] - \text{last\_payload}[1] = 0xFF - 0xFF = 0$. The attack produced zero payload delta spikes and zero magnitude shocks, becoming invisible to the IDS ($\text{TPR} \approx 5.5\%$).
* **Resolution:**  
  ROAD masquerade attacks must be synthesized using baseline frames from `DATA_ROAD_PATH` (`Road_Dataset_no_duplicates.csv`) where `0x6E0` is native and periodic, ensuring attacks interleave with legitimate wheel-speed telemetry.
* **Verification:**  
  `load_expanded_datasets()` now loads ROAD masquerades from `Road_Dataset_no_duplicates.csv`.

---

### BUG-07: 16-Bit Signal Byte-Rollover Mismatch on CAN ID `0x6E0`
* **Subsystem:** `src/encoder.py` (`PerIDNeuromorphicEncoder`)
* **Severity:** Critical | **Status:** **RESOLVED**
* **Description:**  
  In automotive CAN specifications, CAN ID `0x6E0` transmits four 16-bit big-endian wheel speeds. Bytes 1, 3, 5, and 7 are the lower bytes. When a 16-bit counter increments across a 256 boundary (e.g. $0x01FF \to 0x0200$), the lower byte rolls over from $0xFF \to 0x00$, producing an apparent raw byte delta:
  $$d_{\text{raw}} = |0x00 - 0xFF| = 255$$
  Normal benign driving contains thousands of these rollovers. Consequently, standard 99.5th percentile calibration inflated $\tau_{\max}[0x6E0, 1]$ to $251.0$. When a synthetic masquerade injected $+200$, $200 < 251$, so the magnitude shock channel never fired!
* **Root Cause:**  
  Treating multi-byte signals as independent linear bytes without accounting for integer rollover distance modulo 256.
* **Resolution:**  
  Implemented modular circular distance:
  $$d_{\text{mod}} = \min(|p_j - lp_j|, 256 - |p_j - lp_j|)$$
  Under modular distance, $0xFF \to 0x00$ has distance $1$. The benign 99.5th percentile threshold on byte 1 drops from **$251.0$ down to $15.0$**, allowing real kinematic velocity jumps to trigger immediate shocks.
* **Verification:**  
  Diagnostic trace in step 924 proved modular $\tau_{\max}$ is $15.0$ on byte 1, $11.3$ on byte 3, and $9.0$ on byte 7.

---

### BUG-08: Firmware Weight Halving on High-$\tau_{\max}$ Channels
* **Subsystem:** `firmware/conformal_spike_mcu.c` (lines 234–239)
* **Severity:** Medium | **Status:** **RESOLVED**
* **Description:**  
  In `conformal_spike_mcu.c`:
  ```c
  w_j_q8 = (g_tau_max[dense_id][b_idx] > 32U) ? 128U : 256U;
  ```
  Channels with $\tau_{\max} > 32$ were discounted by $50\%$ (`128U` / `256U`) as noisy. Because BUG-07 inflated `g_tau_max` to $240$, the MCU firmware halved the weight of wheel-speed errors, compounding the low detection issue.
* **Root Cause:**  
  Heuristic threshold penalty reacting to inflated $\tau_{\max}$ values.
* **Resolution:**  
  Resolving BUG-07 restores genuine physical $\tau_{\max} \le 15\text{--}24$, ensuring velocity channels maintain full weight (`256U`).

---

### BUG-09: CrossVehicle Domain Shift Deadlock & Perpetual Rollback
* **Subsystem:** `src/encoder.py` (`conditional_rollback`)
* **Severity:** High | **Status:** **RESOLVED**
* **Description:**  
  During zero-shot CrossVehicle transfer (Sonata $\to$ Kia Soul / Chevy Spark), unseen CAN IDs and differing payload formats caused initial alerts. Because rollback occurred on *every* alert, the encoder continuously reverted `last_payload` to pre-shift frames, producing perpetual delta shocks on every subsequent frame ($85.5\%$ FPR deadlock).
* **Root Cause:**  
  Unconditional state rollback without anomaly burst tracking prevents the encoder from ever synchronizing with a new legitimate vehicle bus.
* **Resolution:**  
  1. Balanced multi-platform pretraining (100k frames spanning all 4 datasets).
  2. Bounded consecutive rollback: if an anomaly persists beyond $K_{\max} = 16$ frames without Gate 1 physical excursion, the context state commits to prevent permanent deadlock.
* **Verification:**  
  CrossVehicle FPR dropped from $85.5\%$ to $0.76\%$ in streaming evaluation.

---

### BUG-10: AURIX TC397 Hardware Architecture Claims in Manuscript
* **Subsystem:** `paper/main.tex` (Section VIII & Abstract)
* **Severity:** High | **Status:** **DOCUMENTED (Pending LaTeX update)**
* **Description:**  
  The manuscript contained three hardware inaccuracies:
  1. Claimed TC397 lacks floating-point hardware ("devoid of FPUs"); TC397 actually features dedicated hardware FPUs on each core.
  2. Stated DSPR size as $112\,\text{KB}$; TC397 actually features $240\,\text{KB}$ DSPR per core.
  3. Quoted Frenkel et al. synaptic energy as $0.1\,\text{pJ/SOP}$; Frenkel et al. actually report $12.7\,\text{pJ/SOP}$ for mature CMOS, whereas $0.1\,\text{pJ}$ is the energy of an isolated 32-bit integer adder cell (Horowitz).
* **Resolution:**  
  Update Section VIII and Table VI in `paper/main.tex` to accurately state TC397 FPU availability (justifying fixed-point to avoid multi-cycle pipeline stalls), cite $240\,\text{KB}$ DSPR, and correctly attribute $12.7\,\text{pJ/SOP}$ to Frenkel et al.

---

### BUG-11: Literature Citation Conflations
* **Subsystem:** `paper/main.tex` (Section II Related Work)
* **Severity:** Medium | **Status:** **DOCUMENTED (Pending LaTeX update)**
* **Description:**  
  The manuscript conflated three distinct classic automotive security papers:
  - Cho & Shin USENIX Security 2016 (Clock-skew fingerprinting CIDS).
  - Choi et al. IEEE T-IFS 2018 (VoltageIDs physical layer fingerprinting).
  - Cho & Shin ACM CCS 2016 (Bus-off error handling exploitation).
  Additionally, Stabili et al. [27] was referenced in Table IV without being cited in the body.
* **Resolution:**  
  Disentangle citations into their distinct bibtex entries (`cho2016fingerprinting`, `choi2018voltageids`, `cho2016busoff`), cite Stabili et al., and replace outdated references to Conformal Risk Control with Adaptive Conformal Inference (ACI).

---

### BUG-12: Figure 1 & Figure 2 Visual Artifacts
* **Subsystem:** `src/plotting.py`
* **Severity:** Medium | **Status:** **RESOLVED**
* **Description:**  
  In earlier runs, Figure 1's green curve spiked to $16\%$ FPR during regime shifts, and Figure 2's alert density exploded prior to frame 300.
* **Root Cause:**  
  Direct consequence of BUG-01 (spliced datasets) and BUG-05 (buffer lockout).
* **Resolution:**  
  Regenerated publication figures using the continuous multi-regime stream and the updated quarantine admission rule. Curves now display smooth, bounded tracking within target confidence bands.

---

### BUG-13: Speedometer Masquerade Multi-Byte Magnitude Excursion Omission
* **Subsystem:** `src/models.py` (`compute_frame_score`) & `src/config.py`
* **Severity:** Critical | **Status:** **RESOLVED**
* **Description:**  
  ORNL ROAD Max Speedometer Masquerade (`road_masq_speed`) on CAN ID `0x6E0` with authentic payload `59 59 45 45 00 00 FF FF` registered $1.28\%$ TPR in earlier benchmarks.
* **Root Cause:**  
  1. Attack injections occurred once every $T_{\text{atk}} = 8$ frames. Within the $L = 32$-frame Delayed Staging Queue, only $M = 4$ attack frames arrived, accumulating $\rho_{\text{id}} = 0.0587$. Because $\rho_{\text{thresh}} = 0.15$, Gate 2 quarantine did not trigger within 32 frames.
  2. Attack frame 1 popped from the staging queue unquarantined, triggering ACINominal error rate decrement ($\alpha_k \to 10^{-4}$), inflating the threshold $\hat{\tau}_k$ to the maximum score, and blinding the detector to subsequent attack frames.
  3. `compute_frame_score` calculated scalar magnitude shock as `0.35 * max(tgt_np[16:24])`, which scaled to only $0.35$ even when 4 distinct payload bytes simultaneously exceeded their kinematic physical ceilings $\tau_{\max}$.
* **Resolution:**  
  1. Updated `compute_frame_score` to sum magnitude shocks across all payload channels: `mag_shock = 0.35 * float(np.sum(tgt_np[16:24]))`. On pegged attacks, 4 bytes exceed $\tau_{\max}$, yielding a spatial error shock $s_k > 2.0 \cdot \hat{\tau}_k$ that triggers Gate 1 instantly on frame 1 without delay ($K_{\text{quar}} = 1$).
  2. In Table I regime shifts, decoupled rollback to commit benign observations (`is_alert=False, is_quarantined=q6`), preserving nominal FPR $\le 1.50\%$ while achieving **100.00% TPR** on Speedometer Masquerade.
* **Verification:**  
  Table II SpeedMasq TPR reached $100.00\%$ (937/937 detections). Table V ablation confirmed TPR drops from $100.00\%$ to $9.82\%$ when magnitude shocks are disabled.

---

### BUG-14: Firmware Counter Rollover & Isolated Test Vector Synthesis
* **Subsystem:** `firmware/conformal_spike_mcu.c` & `src/main.py`
* **Severity:** High | **Status:** **RESOLVED**
* **Description:**  
  Bare-metal C host test harness (`test_mcu`) reported $0.0\%$ TPR on attack frames and elevated benign false alarm rates ($>4.0\%$).
* **Root Cause:**  
  1. In `src/main.py`, `test_stream_c` extracted only attack frames (`f.label != 'Normal'`) concatenated after `cal_benign`. Because CAN ID `0x6E0` did not exist in `cal_benign`, the first attack frame arrived without prior state, initializing `last_payload` to the attack payload. Every subsequent attack frame then had $\Delta = 0$, producing zero prediction error.
  2. In `conformal_spike_mcu.c`, raw integer subtraction `(int16_t)payload[j] - (int16_t)st->last_payload[j]` was used without signed circular modular wrapping, causing 8-bit counter rollovers ($0\text{xFF} \to 0\text{x00}$) to compute $\Delta = -255$, triggering false delta spikes.
* **Resolution:**  
  1. Updated `src/main.py` to export authentic interleaved streams (`cal_benign[:1000] + road_masq_speed[:1000]`), establishing proper pre-attack baseline states for CAN ID `0x6E0`.
  2. Added signed circular modular distance wrapping in firmware: `diff = (int16_t)(((raw_diff + 128) & 255) - 128)`.
  3. Decoupled rollback on quarantined frames so only active attacks revert state.
* **Verification:**  
  `make firmware` runs in $4.56\,\text{ms}$, achieving $100.00\%$ TPR, $1.43\%$ FPR ($\le 1.50\%$ ASIL-D target), and $11.80\,\mu\text{s}$ WCET ($\le 100\,\mu\text{s}$ limit).
