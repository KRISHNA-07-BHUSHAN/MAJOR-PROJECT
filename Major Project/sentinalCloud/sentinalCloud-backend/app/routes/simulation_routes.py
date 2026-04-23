# src/sentinalCloud-backend/app/routes/simulation_routes.py
from fastapi import APIRouter, HTTPException, Request
import random
import asyncio
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Configuration ---
BASE_APP_DIR = Path("/code/app")
DATA_DIR = BASE_APP_DIR / "data"

# --- Label Maps (No Changes) ---
NSL_KDD_LABEL_MAP = {
    0: 'normal', 1: 'neptune', 2: 'smurf', 3: 'back', 4: 'pod', 5: 'teardrop',
    6: 'land', 7: 'ipsweep', 8: 'nmap', 9: 'satan', 10: 'guess_passwd',
    11: 'ftp_write', 12: 'multihop', 13: 'phf', 14: 'warezclient',
    15: 'warezmaster', 16: 'spy', 17: 'buffer_overflow', 18: 'loadmodule',
    19: 'perl', 20: 'rootkit', 21: 'xterm', 22: 'sqlattack'
}
CICIDS_LABEL_MAP = {
    0: 'BENIGN', 1: 'DoS Hulk', 2: 'DoS GoldenEye', 3: 'DoS slowloris',
    4: 'DoS Slowhttptest', 5: 'DoS Heartbleed', 6: 'FTP-Patator',
    7: 'SSH-Patator', 8: 'Web Attack - Brute Force', 9: 'Web Attack - XSS',
    10: 'Web Attack - Sql Injection', 11: 'Infiltration', 12: 'Bot',
    13: 'DDoS', 14: 'PortScan', 15: 'Heartbleed'
}
# --- End of Maps ---

# --- Expected features ---
# !!! VERIFY these are the correct 16 features for your TONIOT model !!!
TONIOT_EXPECTED_FEATURES = [
    'ts', 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto', 'service', 'duration',
    'src_bytes', 'dst_bytes', 'conn_state', 'missed_bytes', 'src_pkts', 'src_ip_bytes',
    'dst_pkts', 'dst_ip_bytes'
]
# NOTE: NSLKDD_EXPECTED_FEATURES list is removed as we pass the full row
NSLKDD_LABEL_COLUMN = 'label'
TONIOT_LABEL_COLUMN = 'type'
CICIDS_LABEL_COLUMN = 'label'
# --- End Feature Definitions ---


# --- UPDATED Helper: Cleans column names, REMOVES verbose logging ---
def get_random_row_csv_sample(filepath: Path) -> Dict[str, Any]:
    """Reads CSV, cleans column names, returns random row dict."""
    try:
        df = pd.read_csv(filepath, low_memory=False)
        if df.empty: raise ValueError(f"Sample CSV file is empty: {filepath.name}")
        original_cols = df.columns.tolist()
        # logger.info(f"Columns FOUND in {filepath.name} (BEFORE cleaning): {original_cols} (Count: {len(original_cols)})") # Removed log
        df.columns = df.columns.str.strip()
        cleaned_cols = df.columns.tolist()
        if original_cols != cleaned_cols: logger.warning(f"Cleaned column names for {filepath.name}. Cleaned: {cleaned_cols}")
        random_row = df.sample(n=1, random_state=random.randint(0,10000)).iloc[0].to_dict()
        for key, value in random_row.items():
              if isinstance(value, np.generic): random_row[key] = value.item()
        return random_row
    except Exception as e:
        logger.error(f"Error reading sample CSV {filepath.name}: {e}", exc_info=True)
        raise ValueError(f"Failed to sample from {filepath.name}") from e
# --- End Helper ---


# --- API Endpoints ---
@router.post("/static")
async def simulate_static_attack(request: Request) -> Dict[str, Any]:
    # --- This section finds available CSVs and samples a row (No changes needed here) ---
    # ... (Keep the logic for finding files, sampling loop, and extracting true_label) ...
    await asyncio.sleep(0.05)
    dataset_map = getattr(request.app.state, 'dataset_map', [])
    if not dataset_map: raise HTTPException(status_code=500, detail="Server config error: Dataset map missing.")
    available_sim_entries = []
    for item in dataset_map:
        sample_filenames = item.get('sample_files', [])
        if not sample_filenames and item.get('sample_file'): sample_filenames = [item.get('sample_file')]
        found_files_for_item = []
        for fname in sample_filenames:
            fpath = DATA_DIR / fname
            if fpath.suffix.lower() != '.csv': continue
            if fpath.exists(): found_files_for_item.append(fpath)
        if found_files_for_item: available_sim_entries.append({"key": item['key'],"available_samples": found_files_for_item})
    if not available_sim_entries: raise HTTPException(status_code=500, detail="No usable CSV sample files found.")
    chosen_entry = None; chosen_file_path = None; chosen_file_name = None
    random_row_full = None; true_label = "Unknown"; chosen_model_key = None
    MAX_SAMPLING_ATTEMPTS = 5; attempt = 0
    payload = await request.json() if request.method == "POST" and await request.body() else {}
    desired_type = payload.get("desired_type")
    while attempt < MAX_SAMPLING_ATTEMPTS:
        chosen_entry = random.choice(available_sim_entries)
        chosen_model_key = chosen_entry['key']
        chosen_file_path = random.choice(chosen_entry['available_samples'])
        chosen_file_name = chosen_file_path.name
        # logger.info(f"[Attempt {attempt+1}] Sampling: {chosen_file_name} (Key: {chosen_model_key})")
        try:
            random_row_full = get_random_row_csv_sample(chosen_file_path) # Uses updated helper
            true_label = "Unknown"; file_name_lower = chosen_file_name.lower()
            if TONIOT_LABEL_COLUMN in random_row_full: true_label = str(random_row_full[TONIOT_LABEL_COLUMN])
            elif CICIDS_LABEL_COLUMN in random_row_full and 'cicids' in file_name_lower:
                label_val = int(random_row_full[CICIDS_LABEL_COLUMN]); true_label = CICIDS_LABEL_MAP.get(label_val, f"Unknown_CIC({label_val})")
            elif NSLKDD_LABEL_COLUMN in random_row_full and 'nsl_kdd' in file_name_lower:
                 label_val = int(random_row_full[NSLKDD_LABEL_COLUMN]); true_label = NSL_KDD_LABEL_MAP.get(label_val, f"Unknown_NSL({label_val})")
            # logger.info(f"[Attempt {attempt+1}] Label: {true_label}")
            if not desired_type: break
            current_sample_is_attack = true_label.lower() not in ["normal", "benign", "unknown"]
            matches = (desired_type == "attack" and current_sample_is_attack) or \
                      (desired_type == "normal" and not current_sample_is_attack)
            if matches: logger.info(f"Sample matches desired '{desired_type}'."); break
            attempt += 1
            if attempt >= MAX_SAMPLING_ATTEMPTS: logger.warning(f"Could not find matching sample after {MAX_SAMPLING_ATTEMPTS} attempts."); break
        except ValueError as e:
            logger.error(f"ValueError during sampling attempt {attempt+1} from {chosen_file_name}: {e}")
            attempt += 1;
            if attempt >= MAX_SAMPLING_ATTEMPTS: raise HTTPException(status_code=500, detail=f"Failed to sample valid data.")
            continue
    # --- End Sampling Loop ---

    # --- UPDATED: Feature Extraction Logic ---
    features_for_model = {}
    try:
        sampled_keys = list(random_row_full.keys())
        logger.info(f"Preparing features for model '{chosen_model_key}'. Keys available count: {len(sampled_keys)}")

        if chosen_model_key == 'TONIOT':
            # Selects the 16 features defined in TONIOT_EXPECTED_FEATURES
            missing_cols = [col for col in TONIOT_EXPECTED_FEATURES if col not in random_row_full]
            if missing_cols: raise ValueError(f"Missing required TONIOT features: {missing_cols}")
            features_for_model = {k: random_row_full[k] for k in TONIOT_EXPECTED_FEATURES}
            expected_count = 16
            if len(features_for_model) != expected_count:
                 raise ValueError(f"Incorrect final feature count for TONIOT. Expected {expected_count}, got {len(features_for_model)}.")

        elif chosen_model_key == 'NSLKDD':
            # --- UPDATED: Pass the full row, let preprocessor handle it ---
            logger.info("Passing full row data for NSLKDD to detection route.")
            features_for_model = random_row_full.copy() # Send all columns
            # The preprocessor downstream MUST correctly drop 'label' to get 41 features.
            # Then detection_routes MUST handle the 41 -> (1, 40, 1) reshape.

        elif chosen_model_key == 'CICIDS2017':
             # Keep existing logic for CICIDS (drop label here)
             if CICIDS_LABEL_COLUMN not in random_row_full:
                 logger.warning(f"CICIDS label column '{CICIDS_LABEL_COLUMN}' not found. Using all columns.")
                 features_for_model = random_row_full.copy()
             else:
                features_for_model = {k: v for k, v in random_row_full.items() if k != CICIDS_LABEL_COLUMN}
             logger.info(f"CICIDS features extracted (label dropped): {len(features_for_model)}")

        else: # Unknown model key
             known_labels = [TONIOT_LABEL_COLUMN, CICIDS_LABEL_COLUMN, NSLKDD_LABEL_COLUMN]
             features_for_model = {k: v for k, v in random_row_full.items() if k not in known_labels}
             logger.warning(f"Unknown model key '{chosen_model_key}'. Excluding known labels ({len(features_for_model)} features).")

        logger.info(f"FINAL: Returning {len(features_for_model)} features for model '{chosen_model_key}'")
        return {
            "message": f"Sampled data from {chosen_file_name}", "data": features_for_model,
            "source": chosen_file_name, "model_key": chosen_model_key, "label": true_label
        }
    except ValueError as ve:
        logger.error(f"ValueError preparing features for model {chosen_model_key} from {chosen_file_name}: {ve}", exc_info=False)
        raise HTTPException(status_code=500, detail=f"Internal server error preparing features: {ve}")
    except Exception as e:
         logger.error(f"Unexpected error preparing features for model {chosen_model_key} from {chosen_file_name}: {e}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Unexpected internal server error preparing features.")
    # --- End Feature Extraction & Return ---
