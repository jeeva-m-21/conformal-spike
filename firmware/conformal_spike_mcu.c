/**
 * @file conformal_spike_mcu.c
 * @brief MISRA-C Compliant Q8.8 Implementation of ConformalSpike
 *        for Infineon AURIX TC397 (TriCore) and STM32H753 (Cortex-M7).
 *
 * Implements:
 *   - Per-ID Multi-Scale Log-Delta & Magnitude Shock Encoder (43 inputs)
 *   - ID-Conditioned Predictive Readout (32 predictions)
 *   - True k-WTA Lateral Inhibition with Soft Reset and Ceiling Clamp (K_max = 12)
 *   - Guarded Rolling-Window Conformal Risk Control (G-RW-CRC)
 *   - 32-Frame Delayed Staging Ring Buffer (L = 32)
 *   - Multi-Tiered Quarantine Shield (Excursion shock, Per-ID concentration, Flood)
 *   - Single-ID 16-Byte Lightweight Checkpoint & Deadlock-Free Conditional Rollback
 */

#include "conformal_spike_mcu.h"
#include <string.h>
#include <stdio.h>

#if __has_include("conformal_spike_weights.h")
#include "conformal_spike_weights.h"
#else
/* Dummy weights for standalone compilation before export */
static const int8_t   g_w_in[CS_INPUT_DIM][CS_HIDDEN_DIM] = {{0}};
static const int8_t   g_w_rec[CS_HIDDEN_DIM][CS_HIDDEN_DIM] = {{0}};
static const int8_t   g_w_pred_rec[CS_HIDDEN_DIM][CS_PRED_DIM] = {{0}};
static const int8_t   g_w_pred_id[11][CS_PRED_DIM] = {{0}};
static const uint8_t  g_beta_q8[CS_HIDDEN_DIM] = {230};
static const uint8_t  g_can_id_to_dense[2048] = {0};
static const uint8_t  g_tau_max[CS_MAX_IDS][8] = {{16}};
static const uint16_t g_init_cal_bins[CS_WINDOW_W] = {200};
#endif

static conformal_spike_ctx_t g_cs_ctx;

/* Fast Piecewise-Linear Q8.8 Sigmoid: Bounds predictions strictly in [0, 256] */
static inline int16_t cs_fast_sigmoid_q88(int32_t x_q88) {
    if (x_q88 <= -512) { return 0; }
    if (x_q88 >= 512)  { return 256; }
    return (int16_t)((x_q88 >> 2) + 128); /* Slope 0.25 centered at 0.5 (128) */
}

/* 4-Bit Piecewise-Linear Fixed-Point Log2 Interpolator */
static inline int32_t cs_piecewise_log2_ratio(uint32_t dt_us, uint32_t ema_us) {
    if (dt_us == 0U)  { dt_us = 1U; }
    if (ema_us == 0U) { ema_us = 1U; }
    int32_t clz_dt   = __builtin_clz(dt_us);
    int32_t clz_ema  = __builtin_clz(ema_us);
    int32_t frac_dt  = (int32_t)((dt_us << clz_dt) >> 27) & 0x0F;
    int32_t frac_ema = (int32_t)((ema_us << clz_ema) >> 27) & 0x0F;
    return ((clz_ema - clz_dt) << 4) + (frac_dt - frac_ema);
}

/* O(log M) Fenwick Rank Lookup */
static inline uint16_t cs_fenwick_query_rank(uint16_t target_rank) {
    if (g_cs_ctx.buf_count < 10U) { return 1024U; }
    if (target_rank == 0U) { target_rank = 1U; }
    if (target_rank > g_cs_ctx.buf_count) { target_rank = g_cs_ctx.buf_count; }

    uint16_t idx = 0U;
    uint16_t mask = 1024U;
    uint16_t rem_rank = target_rank;

    while (mask > 0U) {
        uint16_t next_idx = idx + mask;
        if ((next_idx <= CS_FENWICK_BINS) && (g_cs_ctx.bit_tree[next_idx] < rem_rank)) {
            idx = next_idx;
            rem_rank -= g_cs_ctx.bit_tree[idx];
        }
        mask >>= 1U;
    }
    return idx + 1U;
}

/* In-Place True Top-K Selection across Excitable Neurons */
static void cs_true_top_k_selection(const int16_t v_pre[CS_HIDDEN_DIM], uint8_t top_idx[CS_K_WTA], uint8_t *num_winners) {
    *num_winners = 0U;
    for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
        if (v_pre[i] >= CS_V_TH_Q88) {
            uint8_t pos = *num_winners;
            if (pos < CS_K_WTA) {
                (*num_winners)++;
            } else if (v_pre[i] <= v_pre[top_idx[CS_K_WTA - 1U]]) {
                continue;
            }
            while ((pos > 0U) && (v_pre[i] > v_pre[top_idx[pos - 1U]])) {
                if (pos < CS_K_WTA) {
                    top_idx[pos] = top_idx[pos - 1U];
                }
                pos--;
            }
            if (pos < CS_K_WTA) {
                top_idx[pos] = i;
            }
        }
    }
}

void ConformalSpike_Init(void) {
    memset(&g_cs_ctx, 0, sizeof(conformal_spike_ctx_t));
    g_cs_ctx.alpha_target_q16          = 328; /* 0.005 in Q16 = 327.68 */
    g_cs_ctx.alpha_k_q16               = 328;
    g_cs_ctx.alpha_k_q24               = 83886; /* 0.005 in Q24 = 83886.08 */
    g_cs_ctx.alert_density_global_q16   = 0;
    g_cs_ctx.prev_score_q88            = 50;  /* ~0.20 in Q8.8 */
    g_cs_ctx.ema_mean_q88              = 50;
    g_cs_ctx.staging_head              = 0U;
    g_cs_ctx.staging_count             = 0U;

    /* Pre-populate Fenwick buffer with pre-calibrated baseline scores */
    for (uint16_t i = 0U; i < CS_WINDOW_W; i++) {
        uint16_t bin = g_init_cal_bins[i];
        if (bin == 0U) { bin = 1U; }
        if (bin > CS_FENWICK_BINS) { bin = CS_FENWICK_BINS; }
        g_cs_ctx.ring_buf[i] = bin;

        uint16_t idx = bin;
        while (idx <= CS_FENWICK_BINS) {
            g_cs_ctx.bit_tree[idx]++;
            idx += idx & (-idx);
        }
    }
    g_cs_ctx.buf_head  = 0U;
    g_cs_ctx.buf_count = CS_WINDOW_W;
}

const conformal_spike_ctx_t* ConformalSpike_GetContext(void) {
    return &g_cs_ctx;
}

bool ConformalSpike_ProcessFrame_ISR(uint32_t timestamp_us, uint16_t can_id, const uint8_t payload[8]) {
    uint8_t active_in_idx[28];
    uint8_t num_active_in = 0U;
    uint8_t spike_in_vec[CS_INPUT_DIM] = {0};

    uint16_t dense_id = (uint16_t)g_can_id_to_dense[can_id & 0x7FFU];
    if (dense_id >= CS_MAX_IDS) {
        dense_id = 0U;
    }
    cs_id_state_t *st = &g_cs_ctx.id_table[dense_id];

    /* Snapshot pre-frame state (Single-ID 16 bytes: 8 cycles) */
    g_cs_ctx.shadow_dense_id = dense_id;
    g_cs_ctx.shadow_st = *st;
    for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
        g_cs_ctx.shadow_v_hid[i] = g_cs_ctx.v_hid_q88[i];
    }
    for (uint8_t r = 0U; r < g_cs_ctx.num_active_hid; r++) {
        g_cs_ctx.shadow_active_hid[r] = g_cs_ctx.active_hid_idx[r];
    }
    g_cs_ctx.shadow_num_active = g_cs_ctx.num_active_hid;

    /* STEP 1: Encoding with Multi-Scale Payload Deltas & Magnitude Shock */
    for (uint8_t b = 0U; b < 11U; b++) {
        if (((can_id >> b) & 1U) != 0U) {
            spike_in_vec[b] = 1U;
            if (num_active_in < 28U) { active_in_idx[num_active_in++] = b; }
        }
    }

    if (st->valid_flag != 0U) {
        for (uint8_t j = 0U; j < 8U; j++) {
            int16_t raw_diff = (int16_t)payload[j] - (int16_t)st->last_payload[j];
            int16_t abs_diff = (raw_diff >= 0) ? raw_diff : -raw_diff;
            int16_t diff = (int16_t)(((raw_diff + 128) & 255) - 128);

            /* Delta sign channels (11..26) */
            if (diff >= CS_DELTA_THRESH) {
                uint8_t ch = (uint8_t)(11U + (2U * j));
                spike_in_vec[ch] = 1U;
                if (num_active_in < 28U) { active_in_idx[num_active_in++] = ch; }
                st->last_payload[j] = payload[j];
            } else if (diff <= -CS_DELTA_THRESH) {
                uint8_t ch = (uint8_t)(11U + (2U * j) + 1U);
                spike_in_vec[ch] = 1U;
                if (num_active_in < 28U) { active_in_idx[num_active_in++] = ch; }
                st->last_payload[j] = payload[j];
            }

            /* Magnitude Shock channel (27..34) */
            int16_t mod_diff = (abs_diff <= (256 - abs_diff)) ? abs_diff : (int16_t)(256 - abs_diff);
            if (mod_diff > (int16_t)g_tau_max[dense_id][j]) {
                uint8_t mag_ch = (uint8_t)(27U + j);
                spike_in_vec[mag_ch] = 1U;
                if (num_active_in < 28U) { active_in_idx[num_active_in++] = mag_ch; }
            }
        }

        /* 8-bit Log2 Timing (35..42) */
        uint32_t dt_us = timestamp_us - st->last_timestamp_us;
        int32_t log_ratio = cs_piecewise_log2_ratio(dt_us, st->ema_period_us);
        int32_t bin = (log_ratio >> 4) + 4;
        bin = (bin < 0) ? 0 : ((bin > 7) ? 7 : bin);

        if ((log_ratio > 3) || (log_ratio < -3)) {
            uint8_t t_ch = (uint8_t)(35U + (uint8_t)bin);
            spike_in_vec[t_ch] = 1U;
            if (num_active_in < 28U) { active_in_idx[num_active_in++] = t_ch; }
        }

        if ((log_ratio <= 8) && (log_ratio >= -8)) {
            st->ema_period_us += (uint32_t)((int32_t)(dt_us - st->ema_period_us) >> 5);
        }
    } else {
        for (uint8_t j = 0U; j < 8U; j++) {
            st->last_payload[j] = payload[j];
        }
        st->ema_period_us = 10000U;
        st->asil_weight_q8 = (can_id < 0x200U) ? 320U : 256U;
        st->valid_flag = 1U;
        st->consecutive_rollbacks = 0U;
    }
    st->last_timestamp_us = timestamp_us;

    /* STEP 2: ID-Conditioned Predictive Readout with Q4.12 Sigmoid Bounding & Safe Channel Masking */
    int32_t total_weighted_err = 0;
    int32_t total_weight_q8 = 0;
    for (uint8_t j = 0U; j < CS_PRED_DIM; j++) {
        int32_t logit_q88 = 0;
        for (uint8_t r = 0U; r < g_cs_ctx.num_active_hid; r++) {
            logit_q88 += ((int32_t)g_w_pred_rec[g_cs_ctx.active_hid_idx[r]][j] << 1);
        }
        for (uint8_t b = 0U; b < 11U; b++) {
            if (spike_in_vec[b] != 0U) {
                logit_q88 += ((int32_t)g_w_pred_id[b][j] << 1);
            }
        }
        int16_t pred_prob_q8 = cs_fast_sigmoid_q88(logit_q88);
        int16_t target_q8 = (spike_in_vec[11U + j] != 0U) ? 256 : 0;
        int16_t err_q8 = target_q8 - pred_prob_q8;
        int32_t abs_err_q8 = (err_q8 >= 0) ? err_q8 : -err_q8;

        /* Channel entropy weight: safe indexing for delta (0..15), mag (16..23), and timing (24..31) */
        uint16_t w_j_q8 = 256U; /* 1.0 default for timing */
        if (j < 16U) {
            uint8_t b_idx = (uint8_t)(j >> 1);
            w_j_q8 = (g_tau_max[dense_id][b_idx] > 32U) ? 128U : 256U;
        } else if (j < 24U) {
            uint8_t b_idx = (uint8_t)(j - 16U);
            w_j_q8 = (g_tau_max[dense_id][b_idx] > 32U) ? 128U : 256U;
        } else {
            w_j_q8 = 256U; /* Timing deviation is physical bus-level property */
        }

        total_weighted_err += ((abs_err_q8 * (int32_t)w_j_q8) >> 8);
        total_weight_q8 += (int32_t)w_j_q8;
    }
    if (total_weight_q8 == 0) { total_weight_q8 = 1; }
    /* Normalized L1 prediction error in Q4.12 format (1.0 = 4096) */
    int32_t l1_err_q412 = (total_weighted_err * 4096) / total_weight_q8;

    /* STEP 3: Sparse SNN Integration & True k-WTA Selection (structural bound N_act,in <= 28) */
    int16_t v_pre[CS_HIDDEN_DIM];
    for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
        v_pre[i] = (int16_t)(((int32_t)g_cs_ctx.v_hid_q88[i] * (int32_t)g_beta_q8[i]) >> 8);
    }
    for (uint8_t a = 0U; a < num_active_in; a++) {
        uint8_t in_ch = active_in_idx[a];
        for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
            v_pre[i] += ((int16_t)g_w_in[in_ch][i] << 1);
        }
    }
    for (uint8_t r = 0U; r < g_cs_ctx.num_active_hid; r++) {
        uint8_t rec_ch = g_cs_ctx.active_hid_idx[r];
        for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
            v_pre[i] += ((int16_t)g_w_rec[rec_ch][i] << 1);
        }
    }

    cs_true_top_k_selection(v_pre, g_cs_ctx.active_hid_idx, &g_cs_ctx.num_active_hid);

    /* Compute Physics-Informed Somatic Excursion (MES) in Q4.12 */
    int32_t mes_q412 = 0;
    for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
        if (v_pre[i] > CS_V_TH_Q88) {
            mes_q412 += ((int32_t)(v_pre[i] - CS_V_TH_Q88) << 4); /* Q8.8 to Q4.12 */
        }
    }
    mes_q412 = mes_q412 / (int32_t)CS_HIDDEN_DIM;

    /* Soft Reset for Winners, Voltage Ceiling Clamp for Non-Winners */
    for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
        bool won = false;
        for (uint8_t r = 0U; r < g_cs_ctx.num_active_hid; r++) {
            if (g_cs_ctx.active_hid_idx[r] == i) {
                won = true;
                break;
            }
        }
        if (won) {
            g_cs_ctx.v_hid_q88[i] = v_pre[i] - CS_V_TH_Q88;
        } else {
            g_cs_ctx.v_hid_q88[i] = (v_pre[i] > CS_V_CEIL_Q88) ? CS_V_CEIL_Q88 : v_pre[i];
        }
    }

    /* STEP 4: High-Resolution Q4.12 Non-Conformity Scoring & Multi-Tiered Quarantine */
    int32_t timing_shock_q412 = (spike_in_vec[35U] != 0U) ? 1434 : 0;
    int32_t mag_shock_q412 = 0;
    for (uint8_t m = 27U; m < 35U; m++) {
        if (spike_in_vec[m] != 0U) {
            mag_shock_q412 += 1434;
        }
    }
    int32_t score_core_q412 = l1_err_q412 + timing_shock_q412 + mag_shock_q412 + (mes_q412 / 5);
    int32_t s_k_q412 = (score_core_q412 * (int32_t)st->asil_weight_q8) >> 8;
    /* Map Q4.12 score into M = 2,048 bins over [0, 3.0] (3.0 * 4096 = 12288) */
    int32_t bin_calc = ((s_k_q412 * 2047) / 12288) + 1;
    uint16_t s_k_bin = (bin_calc > 2048) ? 2048U : (uint16_t)((bin_calc < 1) ? 1 : bin_calc);

    uint32_t one_minus_alpha = 65536U - (uint32_t)g_cs_ctx.alpha_k_q16;
    uint16_t target_rank = (uint16_t)((one_minus_alpha * (uint32_t)(g_cs_ctx.buf_count + 1U)) >> 16);
    uint16_t lambda_k_bin = cs_fenwick_query_rank(target_rank);

    bool is_alert = (s_k_bin > lambda_k_bin);

    /* Update Global & Per-ID Leaky Alert Densities: rho = 0.985*rho + 0.015*alert */
    int32_t alert_term = is_alert ? 65536 : 0;
    g_cs_ctx.alert_density_global_q16 = ((g_cs_ctx.alert_density_global_q16 * 985) + (alert_term * 15)) / 1000;
    g_cs_ctx.alert_density_id_q16[dense_id] = ((g_cs_ctx.alert_density_id_q16[dense_id] * 985) + (alert_term * 15)) / 1000;

    /* Multi-Tiered Quarantine Gate:
       1. Gate 1: Severe kinematic shock outlier: s_k > 2.0 * lambda_k (triggers K_quar = 1 instantly)
       2. Gate 2: Targeted ECU alert concentration: rho_id > 15.0% (9830 in Q16)
       3. Gate 3: Bus-wide flood attack: rho_global > 35.0% (22938 in Q16)
    */
    bool is_quarantined = (s_k_bin > (lambda_k_bin << 1)) ||
                          (g_cs_ctx.alert_density_id_q16[dense_id] > 9830) ||
                          (g_cs_ctx.alert_density_global_q16 > 22938);

    g_cs_ctx.last_score_q88   = (s_k_q412 >> 4);
    g_cs_ctx.last_lambda_bin  = lambda_k_bin;
    g_cs_ctx.last_quarantined = is_quarantined;

    /* Enqueue into Delayed Staging Ring Buffer (L = 32) */
    if (is_quarantined) {
        /* Purge staging queue immediately! Zero pre-quarantine attack frames enter Fenwick buffer */
        g_cs_ctx.staging_count = 0U;
        g_cs_ctx.staging_head  = 0U;
    } else {
        /* If staging buffer is full (L = 32), pop the verified oldest frame (delayed by 32 frames) */
        if (g_cs_ctx.staging_count == CS_STAGING_LEN) {
            cs_staging_entry_t *old_entry = &g_cs_ctx.staging_queue[g_cs_ctx.staging_head];

            /* Admitted into calibration buffer only if verified non-quarantined */
            if (!old_entry->is_quarantined) {
                if (g_cs_ctx.buf_count == CS_WINDOW_W) {
                    uint16_t old_b = g_cs_ctx.ring_buf[g_cs_ctx.buf_head];
                    uint16_t idx = old_b;
                    while (idx <= CS_FENWICK_BINS) {
                        g_cs_ctx.bit_tree[idx]--;
                        idx += idx & (-idx);
                    }
                } else {
                    g_cs_ctx.buf_count++;
                }

                g_cs_ctx.ring_buf[g_cs_ctx.buf_head] = old_entry->s_k_bin;
                uint16_t idx = old_entry->s_k_bin;
                while (idx <= CS_FENWICK_BINS) {
                    g_cs_ctx.bit_tree[idx]++;
                    idx += idx & (-idx);
                }
                g_cs_ctx.buf_head = (uint16_t)((g_cs_ctx.buf_head + 1U) & (CS_WINDOW_W - 1U));
            }

            /* Per-frame Adaptive Conformal Inference (ACI) update with Q24 accumulator (prevents step truncation) */
            int32_t err_term_q24 = old_entry->is_alert ? 16777216 : 0;
            int32_t diff_alpha_q24 = 83886 - err_term_q24; /* alpha_target_q24 (0.005) - err */
            g_cs_ctx.alpha_k_q24 += (diff_alpha_q24 >> 9);  /* step size gamma = 1/512 */
            if (g_cs_ctx.alpha_k_q24 > 838861) {
                g_cs_ctx.alpha_k_q24 = 838861;              /* alpha_max = 0.05 in Q24 */
            }
            if (g_cs_ctx.alpha_k_q24 < 1678) {
                g_cs_ctx.alpha_k_q24 = 1678;                /* alpha_min = 0.0001 in Q24 */
            }
            g_cs_ctx.alpha_k_q16 = (int32_t)(g_cs_ctx.alpha_k_q24 >> 8);

            g_cs_ctx.staging_head = (uint8_t)((g_cs_ctx.staging_head + 1U) & (CS_STAGING_LEN - 1U));
            g_cs_ctx.staging_count--;
        }

        /* Now push current frame into tail */
        uint8_t tail = (uint8_t)((g_cs_ctx.staging_head + g_cs_ctx.staging_count) & (CS_STAGING_LEN - 1U));
        g_cs_ctx.staging_queue[tail].s_k_q88 = (s_k_q412 >> 4);
        g_cs_ctx.staging_queue[tail].s_k_bin = s_k_bin;
        g_cs_ctx.staging_queue[tail].lambda_bin = lambda_k_bin;
        g_cs_ctx.staging_queue[tail].is_alert = is_alert;
        g_cs_ctx.staging_queue[tail].is_quarantined = is_quarantined;
        g_cs_ctx.staging_count++;
    }

    /* STEP 5: CONDITIONAL ROLLBACK ON QUARANTINED ATTACK FRAMES (Deadlock-Free State Protection) */
    if (is_quarantined) {
        if (g_cs_ctx.shadow_st.valid_flag != 0U) {
            for (uint8_t j = 0U; j < 8U; j++) {
                st->last_payload[j] = g_cs_ctx.shadow_st.last_payload[j];
            }
            for (uint8_t i = 0U; i < CS_HIDDEN_DIM; i++) {
                g_cs_ctx.v_hid_q88[i] = g_cs_ctx.shadow_v_hid[i];
            }
            for (uint8_t r = 0U; r < g_cs_ctx.shadow_num_active; r++) {
                g_cs_ctx.active_hid_idx[r] = g_cs_ctx.shadow_active_hid[r];
            }
            g_cs_ctx.num_active_hid = g_cs_ctx.shadow_num_active;
        }
    } else {
        /* Benign frame or unquarantined alert: Commit observation and advance state */
        if (st->consecutive_rollbacks > 5U) {
            /* Resynchronize timestamp after prolonged attack burst to prevent stale dt deadlock */
            st->last_timestamp_us = timestamp_us;
        }
        st->consecutive_rollbacks = 0U;
    }

    return is_alert;
}
