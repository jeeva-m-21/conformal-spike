"""
Configuration Constants & Hyperparameters for ConformalSpike IDS.
Target Venue: IEEE Transactions on Information Forensics and Security (T-IFS)
"""

import os
from typing import List

# ============================================================================
# ARCHITECTURAL CONSTANTS
# ============================================================================
CS_MAX_IDS          = 256   # Collision-free dense CAN ID capacity
CS_INPUT_DIM        = 43    # 11 ID + 16 payload delta + 8 mag shock + 8 timing
CS_HIDDEN_DIM       = 64    # Recurrent LIF neurons
CS_PRED_DIM         = 32    # 16 delta + 8 mag shock + 8 timing predictions
CS_K_WTA            = 12    # Top-K lateral inhibition cap
CS_WINDOW_W         = 8192  # Sliding window capacity
CS_FENWICK_BINS     = 2048  # Quantile discretization bins
STAGING_QUEUE_LEN   = 32    # Staging queue length L (absorbs K_quar <= 6 delay)
CS_V_TH             = 1.0   # Somatic threshold
CS_V_CEIL           = 1.5   # Voltage clamp ceiling
CS_DELTA_THRESH     = 4     # Payload delta threshold (LSB)
ALPHA_TARGET        = 0.005 # ASIL-D target FPR = 0.50%
LAMBDA_RHO          = 0.985 # Leaky alert density decay
RHO_THRESH          = 0.15  # Per-ID alert density quarantine threshold (15.0%)
QUARANTINE_KAPPA    = 2.0   # Shock score multiplier (kappa * lambda_k)
GAMMA_BASE          = 0.002 # Base ACI step size
UPDATE_BLOCK_SIZE   = 64    # Epoch/block size for piecewise-constant gamma_k
SEEDS: List[int]    = [42, 43, 44]

# Dataset paths
DATA_STATIONARY_PATH = "data/Attack_Dataset_Stationary_no_duplicates.csv"
DATA_DRIVING_PATH    = "data/Attack_Dataset_Driving_no_duplicates.csv"
DATA_ROAD_PATH       = "data/Road_Dataset_no_duplicates.csv"
DATA_SA_PATH         = "data/Attack_SA_Dataset_no_duplicates.csv"
FIG_DIR              = "figures"
PAPER_FIG_DIR        = "paper/figures"
RESULTS_DIR          = "results"

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(PAPER_FIG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
