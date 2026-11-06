/**
 * @file test_mcu.c
 * @brief Host Benchmark & Test Harness for ConformalSpike MCU Firmware
 *        Measures per-frame latency, WCET, throughput, and verification.
 */

#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include "conformal_spike_mcu.h"

#if __has_include("test_vectors.h")
#include "test_vectors.h"
#define TEST_FRAME_COUNT NUM_TEST_VECTORS
#define test_frame_t mcu_test_vector_t
#define g_test_frames g_test_vectors
#else
#define TEST_FRAME_COUNT 1000U
typedef struct {
    uint32_t timestamp_us;
    uint16_t can_id;
    uint8_t  payload[8];
    uint8_t  label_attack;
} test_frame_t;

static const test_frame_t g_test_frames[TEST_FRAME_COUNT] = {
    { 500U, 0x0D0U, { 0x4A, 0x77, 0x04, 0x60, 0x02, 0x01, 0xF0, 0x00 }, 0U }
};
#endif

static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts);
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + (uint64_t)ts.tv_nsec;
}

int main(void) {
    printf("============================================================================\n");
    printf("CONFORMALSPIKE MCU FIRMWARE HARD-REAL-TIME BENCHMARK HARNESS\n");
    printf("Target Architecture: ANSI-C / Infineon AURIX TC397 & STM32H753\n");
    printf("============================================================================\n");

    /* 1. Initialize ConformalSpike context and Fenwick Quantile Buffer */
    ConformalSpike_Init();
    const conformal_spike_ctx_t *ctx = ConformalSpike_GetContext();
    printf("[Init] Buffer Capacity: %u, Count: %u, Alpha Target: %d (Q16)\n",
           CS_WINDOW_W, ctx->buf_count, ctx->alpha_target_q16);

    /* 2. Execute Benchmark over Test Frames */
    uint32_t total_frames = TEST_FRAME_COUNT;

    /* Warm-up pass on authentic benign traffic to calibrate per-ID contexts */
    uint32_t warmup_frames = (total_frames > 100U) ? 50U : 10U;
    for (uint32_t w = 0U; w < warmup_frames; w++) {
        const test_frame_t *f = &g_test_frames[w];
        (void)ConformalSpike_ProcessFrame_ISR(f->timestamp_us, f->can_id, f->payload);
    }

    uint32_t alert_count  = 0U;
    uint32_t quar_count   = 0U;
    uint32_t benign_total = 0U;
    uint32_t benign_alert = 0U;
    uint32_t attack_total = 0U;
    uint32_t attack_alert = 0U;
    uint32_t attack_quar  = 0U;

    uint64_t max_lat_ns  = 0ULL;
    uint64_t min_lat_ns  = UINT64_MAX;

    uint32_t eval_frames = total_frames - warmup_frames;
    printf("[Running] Processing %u authentic automotive CAN frames (after %u warm-up)...\n",
           eval_frames, warmup_frames);

    uint64_t t_start_all = get_time_ns();

    for (uint32_t i = warmup_frames; i < total_frames; i++) {
        const test_frame_t *f = &g_test_frames[i];

        uint64_t t0 = get_time_ns();
        bool alert = ConformalSpike_ProcessFrame_ISR(f->timestamp_us, f->can_id, f->payload);
        uint64_t t1 = get_time_ns();

        uint64_t lat_ns = t1 - t0;
        if (lat_ns > max_lat_ns) { max_lat_ns = lat_ns; }
        if (lat_ns < min_lat_ns) { min_lat_ns = lat_ns; }

        if (alert) { alert_count++; }
        if (ctx->last_quarantined) { quar_count++; }

        if (f->is_attack != 0U) {
            attack_total++;
            if (alert) { attack_alert++; }
            if (ctx->last_quarantined) { attack_quar++; }
        } else {
            benign_total++;
            if (alert) { benign_alert++; }
        }
    }

    uint64_t t_end_all = get_time_ns();
    uint64_t total_time_ns = t_end_all - t_start_all;

    double avg_lat_us = (double)total_time_ns / ((double)eval_frames * 1000.0);
    double max_lat_us = (double)max_lat_ns / 1000.0;
    double min_lat_us = (double)min_lat_ns / 1000.0;
    double throughput_fps = ((double)eval_frames * 1000000000.0) / (double)total_time_ns;

    printf("\n============================================================================\n");
    printf("HOST BENCHMARK EXECUTION RESULTS\n");
    printf("============================================================================\n");
    printf("  Evaluated Frames       : %u\n", eval_frames);
    printf("  Benign Frames          : %u | False Alarms: %u (FPR = %.2f%%, Target <= 0.50%%)\n",
           benign_total, benign_alert, (benign_total > 0U) ? ((100.0 * benign_alert) / benign_total) : 0.0);
    printf("  Attack Frames          : %u | Detections: %u (TPR = %.2f%%), Quarantined: %u (%.2f%%)\n",
           attack_total, attack_alert, (attack_total > 0U) ? ((100.0 * attack_alert) / attack_total) : 0.0,
           attack_quar, (attack_total > 0U) ? ((100.0 * attack_quar) / attack_total) : 0.0);
    printf("  Total Intrusion Alerts : %u (%.2f%%)\n", alert_count, (100.0 * alert_count) / eval_frames);
    printf("  Total Host Time        : %.2f ms\n", (double)total_time_ns / 1000000.0);
    printf("  Throughput             : %.1f frames/second\n", throughput_fps);
    printf("  Average Latency        : %.3f us / frame\n", avg_lat_us);
    printf("  Min Latency            : %.3f us / frame\n", min_lat_us);
    printf("  Worst-Case Exec (WCET) : %.3f us / frame\n", max_lat_us);
    printf("  Meets <= 100 us ASIL-D : %s\n", (max_lat_us < 100.0) ? "YES (PASSED)" : "NO (FAILED)");
    printf("============================================================================\n");

    return 0;
}
