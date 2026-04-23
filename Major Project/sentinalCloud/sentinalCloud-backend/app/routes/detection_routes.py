# src/sentinalCloud-backend/app/routes/detection_routes.py
import logging
import uuid
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import json
import os
from datetime import datetime

# --- Imports ---
from app.models.predict import predict_single_model
from app.utils.preprocessing import DataPreprocessor

# --- SHAP IMPORTS ---
try:
    from app.utils.shap_explain import ShapExplainerService
    from app.routes.explainability_routes import get_shap_service
except ImportError:
    logging.error("Could not import SHAP dependencies for detection route.")
    ShapExplainerService = None
    get_shap_service = None

# --- DYNAMIC LABEL MAPS ---
from app.utils.dynamic_label_mapper import (
    NSL_KDD_LABEL_MAP,
    CICIDS_LABEL_MAP,
    TONIOT_LABEL_MAP
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Detection"])


# -------------------------------------------------------
# Dependency Injection → Preprocessor
# -------------------------------------------------------
def get_preprocessor(request: Request) -> DataPreprocessor:
    preprocessor = getattr(request.app.state, 'preprocessor', None)
    if not preprocessor:
        logger.error("Preprocessor not found in app state during request.")
        raise HTTPException(status_code=503, detail="Preprocessor service unavailable.")
    return preprocessor


# -------------------------------------------------------
# Input Model
# -------------------------------------------------------
class DetectInputData(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    features: Dict[str, Any]
    model_key: str


# -------------------------------------------------------
# Main Detection Route (FINAL + CLEAN)
# -------------------------------------------------------
@router.post("")
async def run_detection_single(
    input_data: DetectInputData,
    request: Request,
    preprocessor: DataPreprocessor = Depends(get_preprocessor),
    shap_service: ShapExplainerService = Depends(get_shap_service) if get_shap_service else None
):
    logger.info(f"[Detection] Request received for model_key: {input_data.model_key}")

    # Basic validation
    if not input_data.features:
        raise HTTPException(400, "No feature dictionary provided.")
    if not input_data.model_key:
        raise HTTPException(400, "No model_key provided.")

    # Load models
    models = getattr(request.app.state, 'models', None)
    model_infos = getattr(request.app.state, 'model_infos', None)
    if not models or not model_infos:
        raise HTTPException(503, "Detection models unavailable.")

    model_key = input_data.model_key
    if model_key not in models:
        raise HTTPException(400, f"Invalid model_key '{model_key}'.")

    model = models[model_key]
    model_info = model_infos[model_key]

    try:
        # -------------------------------------------------------
        # 1. Convert dict → dataframe
        # -------------------------------------------------------
        input_df = pd.DataFrame([input_data.features])

        # -------------------------------------------------------
        # 2. Preprocess using your pipeline
        # -------------------------------------------------------
        X_processed = preprocessor.transform(input_df)
        num_features = X_processed.shape[1]

        logger.info(f"[Detection] After preprocessing shape = {X_processed.shape}")

        # Model shape info
        steps = model_info["input_shape"][1]
        f_per_step = model_info["input_shape"][2]
        expected_total = steps * f_per_step

        # Special NSL-KDD fix
        data_to_reshape = X_processed
        if model_key == "NSLKDD":
            if num_features == 41 and expected_total == 40:
                logger.warning("[NSLKDD] Dropping last feature to match 40.")
                data_to_reshape = X_processed[:, :-1]
                num_features = 40

        # -------------------------------------------------------
        # 3. Reshape
        # -------------------------------------------------------
        if num_features == steps and f_per_step == 1:
            X_reshaped = data_to_reshape.reshape(1, steps, 1)
        elif num_features == expected_total:
            X_reshaped = data_to_reshape.reshape(1, steps, f_per_step)
        else:
            raise HTTPException(
                400,
                f"Incompatible feature count: {num_features}, expected {expected_total}"
            )

        X_reshaped = X_reshaped.astype(np.float32)

        # -------------------------------------------------------
        # 4. Predict
        # -------------------------------------------------------
        prediction_label, confidence = predict_single_model(model, X_reshaped)
        logger.info(f"[Detection] Prediction = {prediction_label}, confidence = {confidence}")

        # -------------------------------------------------------
        # 5. Determine Specific Attack Label (NEW)
        # -------------------------------------------------------
        specific_label = "Unknown"

        try:
            raw_pred = model.predict(X_reshaped, verbose=0)[0]
            raw_pred = np.array(raw_pred).flatten()

            raw_idx = int(np.argmax(raw_pred))

            if model_key == "CICIDS2017":
                specific_label = CICIDS_LABEL_MAP.get(raw_idx, f"CIC_Class_{raw_idx}")
            elif model_key == "NSLKDD":
                specific_label = NSL_KDD_LABEL_MAP.get(raw_idx, f"NSL_Class_{raw_idx}")
            elif model_key == "TONIOT":
                specific_label = TONIOT_LABEL_MAP.get(raw_idx, f"ToN_Class_{raw_idx}")

        except Exception as e:
            logger.warning(f"[Detection] Could not extract specific label: {e}")
            specific_label = "Unknown"

        # -------------------------------------------------------
        # 6. SHAP Calculation (unchanged)
        # -------------------------------------------------------
        shap_result = None
        if prediction_label == "Attack" and shap_service:
            try:
                logger.info("[Detection] Generating SHAP explanation...")

                processed_df_for_shap = preprocessor.transform_df(input_df)
                feat_names = processed_df_for_shap.columns.tolist()

                if model_key == "NSLKDD" and len(feat_names) == 41 and data_to_reshape.shape[1] == 40:
                    feat_names = feat_names[:-1]

                shap_df = pd.DataFrame(data_to_reshape, columns=feat_names)

                shap_result = shap_service.explain_sample(
                    sample_df=shap_df,
                    model_name=model_key,
                    top_k=7
                )
            except Exception as se:
                logger.error(f"[SHAP ERROR] {se}")
                shap_result = {"error": str(se)}

        # 7. Build Response
        # -------------------------------------------------------
        event_id = f"evt_{uuid.uuid4()}"
                # ⭐ NEW: SAVE EXPLANATION WITHOUT AFFECTING EXISTING LOGIC
        try:
            save_explanation(
                event_id=event_id,
                raw_label=specific_label,
                features=shap_result.get("features", {}) if shap_result else {},
                shap_values=shap_result.get("shap_values", {}) if shap_result else {},
                shap_image=shap_result.get("image_base64", None) if shap_result else None
            )
            logger.info(f"[XAI] Explanation saved for event: {event_id}")
        except Exception as save_err:
            logger.error(f"[XAI STORE ERROR] Failed to save XAI event: {save_err}")
        # ⭐ END NEW BLOCK


        return {
            "event_id": event_id,
            "prediction": prediction_label,
            "specific_label": specific_label,
            "confidence": confidence,
            "model_used": model_key,
            "shap_explanation": shap_result
        }


    except Exception as e:
        logger.exception(f"[Detection] Unexpected error: {e}")
        raise HTTPException(500, "Internal server error in detection.")
# ------------------------------
#  EXPLAINABILITY (XAI) ROUTES
# ------------------------------

EXPLAIN_STORE_PATH = "app/data/xaistore.json"
ATTACK_GROUPS_PATH = "app/utils/attack_groups.json"
ATTACK_KB_PATH = "app/utils/attack_knowledge_base.json"


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except:
            return {}


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------
# 1. GET LIST OF ALL EXPLAINED EVENTS
# ---------------------------------------------
@router.get("/explain/events")
def get_all_explained_events():
    data = load_json(EXPLAIN_STORE_PATH)

    event_list = []
    for event_id, evt in data.items():
        event_list.append({
            "event_id": event_id,
            "raw_label": evt.get("raw_label", "Unknown"),
            "grouped_label": evt.get("grouped_label", "Unknown"),
            "timestamp": evt.get("timestamp", "Unknown")
        })

    return {"events": event_list}


# ---------------------------------------------
# 2. GET FULL EXPLANATION FOR ONE EVENT
# ---------------------------------------------
@router.get("/explain/event")
def get_explanation(event_id: str):
    data = load_json(EXPLAIN_STORE_PATH)

    if event_id not in data:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"explanation": data[event_id]}


# ---------------------------------------------
# 3. SAVE EXPLANATION (Called by Dashboard)
# ---------------------------------------------
@router.post("/explain/save")
def save_explanation(event_id: str,
                     raw_label: str,
                     features: dict,
                     shap_values: dict = None,
                     shap_image: str = None):

    # -------------------------------
    #  SKIP NORMAL EVENTS COMPLETELY
    # -------------------------------
    if raw_label.lower() in ["normal", "benign"]:
        return {"status": "skipped_normal"}

    store = load_json(EXPLAIN_STORE_PATH)
    groups = load_json(ATTACK_GROUPS_PATH)
    kb = load_json(ATTACK_KB_PATH)

    # Convert raw label → grouped label
    grouped_label = groups.get(raw_label, raw_label)

    # Load theory from KB
    attack_info = kb.get(grouped_label, {
        "meaning": "No description available.",
        "prevention": ["No prevention steps available."]
    })

    # Create event entry
    store[event_id] = {
        "raw_label": raw_label,
        "grouped_label": grouped_label,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "features": features,
        "shap_values": shap_values,
        "shap_image": shap_image,
        "meaning": attack_info.get("meaning"),
        "prevention": attack_info.get("prevention")
    }

    save_json(EXPLAIN_STORE_PATH, store)

    return {"status": "saved", "event_id": event_id}



# ---------------------------------------------
# 4. CLEAR ALL EXPLAINED EVENTS (optional)
# ---------------------------------------------
@router.post("/explain/clear")
def clear_explained_events():
    save_json(EXPLAIN_STORE_PATH, {})
    return {"status": "cleared"}
