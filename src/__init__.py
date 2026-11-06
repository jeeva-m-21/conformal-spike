"""
ConformalSpike: Calibrated Conformal Risk-Controlled Dynamic Thresholding
for In-Vehicle Neuromorphic Intrusion Detection Systems (IDS).
Target Venue: IEEE Transactions on Information Forensics and Security (T-IFS)
"""

from .config import (
    CS_MAX_IDS,
    CS_INPUT_DIM,
    CS_HIDDEN_DIM,
    CS_PRED_DIM,
    CS_K_WTA,
    CS_WINDOW_W,
    CS_FENWICK_BINS,
    STAGING_QUEUE_LEN,
    CS_V_TH,
    CS_V_CEIL,
    CS_DELTA_THRESH,
    ALPHA_TARGET,
    LAMBDA_RHO,
    RHO_THRESH,
    QUARANTINE_KAPPA,
    GAMMA_BASE,
    UPDATE_BLOCK_SIZE,
    SEEDS,
    DATA_STATIONARY_PATH,
    DATA_DRIVING_PATH,
    DATA_ROAD_PATH,
    DATA_SA_PATH,
    FIG_DIR,
    PAPER_FIG_DIR,
    RESULTS_DIR,
)

from .data_loader import (
    CANFrame,
    parse_payload,
    load_expanded_datasets,
)

from .encoder import (
    SingleIDContext,
    PerIDNeuromorphicEncoder,
)

from .models import (
    SuperSpikeSurrogate,
    IDConditionedKWtaSNN,
    pretrain_conformal_spike,
    compute_frame_score,
)

from .conformal import (
    FenwickQuantileBuffer,
    ConformalSpikeIDS,
)

from .baselines import (
    INT8TinyMLPAutoencoder,
    INT8MicroGRU,
    pretrain_baseline_models,
    StatisticalTimingEntropyIDS,
    HeuristicStaticIDS,
    SplitConformalIDS,
    UnguardedOnlineACIIDS,
    AlertGatedOnlineACIIDS,
    NonNeuralDeltaConformalIDS,
)

from .evaluation import (
    compute_bootstrap_ci,
    run_table_i_regime_shifts,
    run_table_ii_attacks,
    run_adversarial_pulse_sweep,
    run_ablation_study,
    run_pulse_attack_simulation,
)

from .plotting import (
    generate_publication_figures,
)

from .mcu_export import (
    export_c_headers,
)

__all__ = [
    # Config
    "CS_MAX_IDS",
    "CS_INPUT_DIM",
    "CS_HIDDEN_DIM",
    "CS_PRED_DIM",
    "CS_K_WTA",
    "CS_WINDOW_W",
    "CS_FENWICK_BINS",
    "STAGING_QUEUE_LEN",
    "CS_V_TH",
    "CS_V_CEIL",
    "CS_DELTA_THRESH",
    "ALPHA_TARGET",
    "LAMBDA_RHO",
    "RHO_THRESH",
    "QUARANTINE_KAPPA",
    "GAMMA_BASE",
    "UPDATE_BLOCK_SIZE",
    "SEEDS",
    "DATA_STATIONARY_PATH",
    "DATA_DRIVING_PATH",
    "DATA_ROAD_PATH",
    "DATA_SA_PATH",
    "FIG_DIR",
    "PAPER_FIG_DIR",
    "RESULTS_DIR",
    # Data Loader
    "CANFrame",
    "parse_payload",
    "load_expanded_datasets",
    # Encoder
    "SingleIDContext",
    "PerIDNeuromorphicEncoder",
    # Models
    "SuperSpikeSurrogate",
    "IDConditionedKWtaSNN",
    "pretrain_conformal_spike",
    "compute_frame_score",
    # Conformal
    "FenwickQuantileBuffer",
    "ConformalSpikeIDS",
    # Baselines
    "INT8TinyMLPAutoencoder",
    "INT8MicroGRU",
    "pretrain_baseline_models",
    "StatisticalTimingEntropyIDS",
    "HeuristicStaticIDS",
    "SplitConformalIDS",
    "UnguardedOnlineACIIDS",
    "AlertGatedOnlineACIIDS",
    "NonNeuralDeltaConformalIDS",
    # Evaluation
    "compute_bootstrap_ci",
    "run_table_i_regime_shifts",
    "run_table_ii_attacks",
    "run_adversarial_pulse_sweep",
    "run_ablation_study",
    "run_pulse_attack_simulation",
    # Plotting
    "generate_publication_figures",
    # MCU Export
    "export_c_headers",
]
