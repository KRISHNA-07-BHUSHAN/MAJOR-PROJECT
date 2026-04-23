# app/utils/dynamic_attack.py

"""
Dynamic attack simulator for SentinelCloud.
Lightweight fixes + pulls label mappings from external file.
"""

import asyncio
import random
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# label mapper (NEW)
from app.utils.dynamic_label_mapper import map_dynamic_label

try:
    from app.models.predict import predict_single_model
except Exception:
    predict_single_model = None

logger = logging.getLogger(__name__)

APP_DATA_DIR = Path("app") / "data"
SAVED_MODELS_DIR = Path("saved_Models")


class DynamicAttackSimulator:
    def __init__(self, app, interval_seconds: float = 3.0):
        self.app = app
        self.interval_seconds = interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

        self.scalers = {}
        self.sample_frames = {}
        self.feature_names = {}

        try:
            self._prepare_scalers()
        except Exception as e:
            logger.warning(f"[DynamicSimulator] Scaler preparation failed: {e}")

    # -----------------------------------------------------------
    def is_running(self) -> bool:
        return self._running

    async def start(self):
        if self._running:
            return {"status": "already_running"}
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("[DynamicSimulator] Started.")
        return {"status": "started"}

    async def stop(self):
        if not self._running:
            return {"status": "not_running"}
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("[DynamicSimulator] Stopped.")
        return {"status": "stopped"}

    # -----------------------------------------------------------
    async def generate_one(self) -> Dict[str, Any]:
        choice = random.choice(["NSL", "CIC", "TON"])
        model_key_map = {"NSL": "NSLKDD", "CIC": "CICIDS2017", "TON": "TONIOT"}
        model_key = model_key_map.get(choice, "CICIDS2017")

        try:
            features_dict = self._synthesize_sample(choice)
        except Exception as e:
            logger.error(f"Sample synthesis error: {e}")
            raise

        detection_result = await self._detect_with_preprocessor(features_dict, model_key)

        event_id = detection_result.get("event_id", f"evt_{uuid.uuid4()}")
        pred_type = detection_result.get("prediction", "Unknown")
        raw_index = detection_result.get("raw_index")
        shap_explanation = detection_result.get("shap_explanation", None)

        # ⭐ UPDATED: Central label mapping
        specific_label = map_dynamic_label(model_key, raw_index)

        event = {
            "event_id": event_id,
            "id": event_id,
            "label": specific_label,
            "specific_label": specific_label,
            "type": pred_type.lower(),
            "time": pd.Timestamp.now().isoformat(),
            "confidence": detection_result.get("confidence", 0.0),
            "features": features_dict,
            "model_used": model_key,
            "sourceFile": "Dynamic Generator",
            "shap_explanation": shap_explanation,
            "raw_index": raw_index
        }

        self._store_event(event)
        logger.info(f"[DynamicSimulator] Generated: {specific_label} ({event_id})")

        return event

    # -----------------------------------------------------------
    async def _run_loop(self):
        while self._running:
            try:
                await self.generate_one()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
            await asyncio.sleep(self.interval_seconds)

    # -----------------------------------------------------------
    def _prepare_scalers(self):
        try:
            nsl = APP_DATA_DIR / "NSL_KDD_Preprocessed_sample.csv"
            if nsl.exists():
                df = pd.read_csv(nsl)
                num = df.select_dtypes(include=[np.number]).iloc[:, :40]
                self.scalers["NSL"] = MinMaxScaler().fit(num)
                self.sample_frames["NSL"] = num
                self.feature_names["NSL"] = list(num.columns)
        except Exception:
            pass

        try:
            cic = APP_DATA_DIR / "CICIDS2017_V2_full_preprocessed_sample.csv"
            if cic.exists():
                df = pd.read_csv(cic)
                num = df.select_dtypes(include=[np.number]).iloc[:, :78]
                self.scalers["CIC"] = MinMaxScaler().fit(num)
                self.sample_frames["CIC"] = num
                self.feature_names["CIC"] = list(num.columns)
        except Exception:
            pass

        try:
            ton = APP_DATA_DIR / "TON_IOT_Firsthalf_sample.csv"
            if ton.exists():
                df = pd.read_csv(ton)
                num = df.select_dtypes(include=[np.number]).iloc[:, :16]
                self.scalers["TON"] = MinMaxScaler().fit(num)
                self.sample_frames["TON"] = num
                self.feature_names["TON"] = list(num.columns)
        except Exception:
            pass

    # -----------------------------------------------------------
    def _synthesize_sample(self, which: str) -> Dict[str, Any]:
        if which not in self.sample_frames:
            arr = np.random.rand(40)
            return {f"f{i}": float(arr[i]) for i in range(40)}

        df = self.sample_frames[which]
        mean = df.mean()
        std = df.std().replace(0, 1)
        sample = np.random.normal(mean.values, std.values)
        cols = self.feature_names.get(which, list(df.columns))

        return {cols[i]: float(sample[i]) for i in range(min(len(cols), len(sample)))}

    # -----------------------------------------------------------
    async def _detect_with_preprocessor(self, features: Dict[str, Any], model_key: str):
        preprocessor = getattr(self.app.state, "preprocessor", None)
        models = getattr(self.app.state, "models", None)
        model_infos = getattr(self.app.state, "model_infos", None)

        if preprocessor is None:
            raise RuntimeError("Preprocessor missing")
        if model_key not in models:
            raise RuntimeError("Model missing")

        model = models[model_key]
        model_info = model_infos[model_key]

        X_processed = preprocessor.transform(features)
        if X_processed.ndim == 1:
            X_processed = X_processed.reshape(1, -1)

        expected_steps = model_info["input_shape"][1]
        expected_feat = model_info["input_shape"][2]
        expected_total = expected_steps * expected_feat

        data = X_processed.copy()
        if data.shape[1] != expected_total:
            data = data[:, :expected_total] if data.shape[1] > expected_total else \
                   np.concatenate([data, np.zeros((1, expected_total - data.shape[1]))], axis=1)

        X = data.reshape(1, expected_steps, expected_feat).astype(np.float32)

        raw_index = None
        arr = None

        try:
            arr = np.array(model.predict(X, verbose=0)[0]).flatten()
            raw_index = int(np.argmax(arr))
        except:
            pass

        pred_label = "Unknown"
        confidence = 0.0
        try:
            p_label, p_conf = predict_single_model(model, X)
            pred_label = p_label
            confidence = p_conf
        except:
            pass

        return {
            "prediction": pred_label,
            "confidence": confidence,
            "raw_index": raw_index,
            "model_used": model_key,
            "event_id": f"evt_{uuid.uuid4()}",
            "shap_explanation": None
        }

    # -----------------------------------------------------------
    def _store_event(self, evt: Dict[str, Any]):
        if not hasattr(self.app.state, "event_cache"):
            self.app.state.event_cache = {}
        self.app.state.event_cache[evt["event_id"]] = evt
