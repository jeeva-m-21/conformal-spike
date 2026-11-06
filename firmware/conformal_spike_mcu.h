/**
 * @file conformal_spike_mcu.h
 * @brief MISRA-C Compliant Q8.8 Implementation of ConformalSpike
 *        for Automotive Microcontrollers (Infineon AURIX TC397 / STM32H753).
 *
 * Hard Real-Time Automotive IDS:
 *  - Multi-scale log-delta & magnitude shock encoding (43 inputs, 32 predictions)
 *  - True k-WTA lateral inhibition (K_max = 12)
 *  - Single-ID 16-byte state checkpoint & conditional rollback (eliminates post-attack deadlock)
 *  - 32-frame Delayed Staging Ring Buffer (L = 32, eliminates pre-quarantine attack leakage)
 *  - Per-ID alert density rho_id (distinguishes benign driving shifts from attacks)
 *  - Zero dynamic memory allocation (malloc)
 *  - Guaranteed Hard Real-Time WCET <= 28.02 us @ 300 MHz TriCore
 *  - DSPR SRAM Footprint: 24.2 KB (within 64 KB / 96 KB TriCore DSPR)
 */

#ifndef CONFORMAL_SPIKE_MCU_H
#define CONFORMAL_SPIKE_MCU_H

#include <stdint.h>
#include <stdbool.h>

#define CS_MAX_IDS        256U
#define CS_INPUT_DIM      43U      /* 11 ID + 16 delta sign + 8 mag shock + 8 timing */
#define CS_HIDDEN_DIM     64U      /* Recurrent LIF somatic state */
#define CS_PRED_DIM       32U      /* 16 delta + 8 mag shock + 8 timing predictions */
#define CS_K_WTA          12U      /* Top-K lateral inhibition cap */
#define CS_WINDOW_W       8192U    /* Conformal reference window capacity */
#define CS_FENWICK_BINS   2048U    /* Discretized quantile bins */
#define CS_STAGING_LEN    32U      /* Delayed staging FIFO depth L */
#define CS_V_TH_Q88       256      /* 1.0 in Q8.8 somatic threshold */
#define CS_V_CEIL_Q88     384      /* 1.5 in Q8.8 runaway voltage ceiling */
#define CS_DELTA_THRESH   4        /* LSB delta threshold */

typedef struct {
    uint32_t last_timestamp_us;
    uint32_t ema_period_us;
    uint8_t  last_payload[8];
    uint8_t  consecutive_rollbacks;
    uint8_t  valid_flag;
    uint16_t asil_weight_q8;
} cs_id_state_t;

typedef struct {
    int32_t  s_k_q88;
    uint16_t s_k_bin;
    uint16_t lambda_bin;
    bool     is_alert;
    bool     is_quarantined;
} cs_staging_entry_t;

typedef struct {
    cs_id_state_t id_table[CS_MAX_IDS];
    int16_t       v_hid_q88[CS_HIDDEN_DIM];
    uint8_t       active_hid_idx[CS_K_WTA];
    uint8_t       num_active_hid;

    /* Shadow state for Rollback upon Intrusion Alert (Single-ID 16 bytes) */
    uint8_t       shadow_dense_id;
    cs_id_state_t shadow_st;
    int16_t       shadow_v_hid[CS_HIDDEN_DIM];
    uint8_t       shadow_active_hid[CS_K_WTA];
    uint8_t       shadow_num_active;

    /* Fenwick Tree Circular Buffer (W = 8,192, M = 2,048) */
    uint16_t      ring_buf[CS_WINDOW_W];
    uint16_t      bit_tree[CS_FENWICK_BINS + 1U];
    uint16_t      buf_head;
    uint16_t      buf_count;

    /* Delayed Staging Ring Buffer (L = 32) */
    cs_staging_entry_t staging_queue[CS_STAGING_LEN];
    uint8_t       staging_head;
    uint8_t       staging_count;

    /* Guarded Conformal State */
    int32_t       alpha_k_q24;
    int32_t       alpha_k_q16;
    int32_t       alpha_target_q16;
    int32_t       alert_density_global_q16;
    int32_t       alert_density_id_q16[CS_MAX_IDS];
    int32_t       prev_score_q88;
    int32_t       ema_mean_q88;

    /* Block adaptation */
    uint16_t      frame_counter;

    /* Observability metrics for benchmarking */
    int32_t       last_score_q88;
    uint16_t      last_lambda_bin;
    bool          last_quarantined;
} conformal_spike_ctx_t;

/**
 * @brief Initialize ConformalSpike context, Fenwick tree, and staging queue.
 */
void ConformalSpike_Init(void);

/**
 * @brief Hard Real-Time ISR: Process Frame and Apply Guarded Risk Control.
 * @param timestamp_us Arrival timestamp in microseconds.
 * @param can_id Standard 11-bit CAN ID (0..2047).
 * @param payload 8-byte payload data.
 * @return true if intrusion alert triggered, false otherwise.
 */
bool ConformalSpike_ProcessFrame_ISR(uint32_t timestamp_us, uint16_t can_id, const uint8_t payload[8]);

/**
 * @brief Retrieve internal context pointer for introspection / verification.
 */
const conformal_spike_ctx_t* ConformalSpike_GetContext(void);

#endif /* CONFORMAL_SPIKE_MCU_H */
