# src/sentinalCloud-backend/app/utils/shap_explain.py
"""
A high-performance, class-based service for generating SHAP explanations.
Explainers are pre-computed on startup to ensure fast API responses.
"""
import logging
from typing import Dict, List, Any

import numpy as np
import pandas as pd
import shap
from tensorflow.keras.models import Model

logger = logging.getLogger(__name__)

class ShapExplainerService:
    """
    Manages the lifecycle of SHAP explainers for all loaded models.
    """
    
    def __init__(self, models: List[Model], model_infos: List[str], background_data: pd.DataFrame):
        self.models = {name: model for model, name in zip(models, model_infos)}
        self.explainers = {}
        # Store initial background columns (used as fallback/reference)
        self.background_data_columns = background_data.columns.tolist() 
        
        logger.info("Initializing SHAP explainers for all models...")
        for model_name in model_infos:
            model = self.models[model_name]
            self._create_explainer(model, model_name)
        logger.info(f"✅ SHAP explainers initialized for {len(self.explainers)} models.")

    def _prediction_function(self, model: Model):
        """
        Wrapper function for a model to be used by KernelExplainer.
        This version handles:
        1. Sigmoid (k, 1)
        2. Binary Softmax (k, 2)
        3. Multi-Class Softmax (k, n_classes)
        """
        def f(x: np.ndarray):
            # 1. Reshape 2D input (n, features) to 3D (n, features, 1) for the model
            if x.ndim == 2: 
                x = np.expand_dims(x, axis=-1)
            
            # 2. Get model predictions
            preds = model.predict(x, verbose=0) 

            # 3. Handle different output shapes
            if preds.ndim == 2:
                num_classes = preds.shape[1]
                
                if num_classes == 1:
                    # Case 1: Sigmoid output (k, 1)
                    return np.atleast_1d(np.squeeze(preds))
                    
                if num_classes == 2:
                    # Case 2: Binary softmax output (k, 2)
                    return preds[:, 1]
                    
                if num_classes > 2:
                    # Case 3: Multi-class output (k, 23)
                    return np.max(preds[:, 1:], axis=1)
            
            # Fallback for unexpected shapes
            return np.atleast_1d(np.squeeze(preds))
            
        return f

    def _create_explainer(self, model: Model, model_name: str):
        """Tries to create a DeepExplainer, falls back to KernelExplainer with safe background handling."""
        model_input_shape = model.input_shape
        num_features = model_input_shape[1] if len(model_input_shape) == 3 else model_input_shape[-1]
        
        background_zeros = np.zeros((10, num_features)) 

        try:
            background_sample_3d = np.expand_dims(background_zeros, axis=-1)
            self.explainers[model_name] = {
                "explainer": shap.DeepExplainer(model, background_sample_3d),
                "method": "DeepExplainer"
            }
            logger.info(f"Created DeepExplainer for model '{model_name}'.")
            return
        except Exception as e:
            logger.warning(f"DeepExplainer failed for '{model_name}' ({e}). Falling back to KernelExplainer.")

        # --- SAFE FALLBACK for KernelExplainer ---
        try:
            background_summary = shap.kmeans(background_zeros, 5)
            summary_data = background_summary.data
        except Exception as e:
            logger.warning(f"KMeans summarization failed for '{model_name}' ({e}). Using raw background data instead.")
            summary_data = background_zeros

        self.explainers[model_name] = {
            "explainer": shap.KernelExplainer(self._prediction_function(model), summary_data),
            "method": "KernelExplainer"
        }
        logger.info(f"Created KernelExplainer for model '{model_name}'. (safe fallback active)")

    # --- THIS FUNCTION IS UPDATED ---
    def _format_shap_values(
        self, 
        shap_values_raw: np.ndarray, 
        feature_names: List[str], 
        original_values: Dict[str, Any], # <-- FIX: Added original_values dictionary
        top_k: int, 
        base_value: float = 0.0,
        final_prediction: float = 0.0
    ) -> Dict:
        
        shap_values = shap_values_raw
        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) == 2 else shap_values[0]
        
        sample_shap = np.squeeze(shap_values)

        if sample_shap.ndim == 0:
             sample_shap = np.array([float(sample_shap)])
        elif sample_shap.ndim > 1:
             sample_shap = np.squeeze(sample_shap)

        if sample_shap.shape[0] != len(feature_names):
            logger.error(f"SHAP format mismatch: Have {sample_shap.shape[0]} SHAP values but {len(feature_names)} feature names.")
            if sample_shap.size == len(feature_names):
                 logger.warning("Reshaping SHAP values to match feature names.")
                 sample_shap = sample_shap.flatten()
            else:
                 raise ValueError(f"Cannot match {sample_shap.shape} SHAP values to {len(feature_names)} features.")

        # --- FIX: Align keys with frontend (name, impact, value) ---
        pairs = [{
            "name": name,
            "impact": float(val),
            "value": original_values.get(name, 'N/A'), # <-- FIX: Get the original value
            "abs_impact": abs(float(val))
        } for name, val in zip(feature_names, sample_shap)]
        
        pairs.sort(key=lambda x: x["abs_impact"], reverse=True)
        top_features = pairs[:top_k]
        
        for p in top_features:
            p["sign"] = "increases_attack" if p["impact"] > 0 else "reduces_attack"
            del p["abs_impact"]

        return {
            "base_value": float(base_value),
            "final_prediction": float(final_prediction),
            "features": top_features,
            "raw_shap_values": sample_shap.tolist(),
            "feature_names": feature_names
        }

    # --- THIS FUNCTION IS UPDATED ---
    def explain_sample(
        self, sample_df: pd.DataFrame, model_name: str, nsamples: int = "auto", top_k: int = 6
    ) -> Dict:
        if model_name not in self.explainers:
            raise ValueError(f"No explainer found for model '{model_name}'.")

        explainer_info = self.explainers[model_name]
        explainer = explainer_info["explainer"]
        method = explainer_info["method"]

        input_feature_names = sample_df.columns.tolist()
        
        # --- FIX: Get the original values from the sample_df ---
        try:
            original_values_dict = sample_df.to_dict(orient='records')[0]
        except Exception:
            logger.warning("Could not extract original values, will default to N/A.")
            original_values_dict = {}
        # --- END FIX ---

        base_value = 0.0
        final_prediction = 0.0
        
        if isinstance(explainer, shap.KernelExplainer):
            input_data = sample_df.values
            if input_data.ndim != 2:
                 logger.warning(f"KernelExplainer input was not 2D, reshaping. Original shape: {input_data.shape}")
                 input_data = input_data.reshape(1, -1)
            
            try:
                base_value = explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
                final_prediction = explainer.model.f(input_data)[0]
            except Exception as e:
                 logger.warning(f"Could not get base/final values for KernelExplainer: {e}")

            raw_shap_values = explainer.shap_values(input_data, nsamples=nsamples)
        else:
            # DeepExplainer
            input_data = np.expand_dims(sample_df.values, axis=-1)
            if input_data.ndim != 3:
                 logger.warning(f"DeepExplainer input was not 3D, reshaping. Original shape: {input_data.shape}")
                 input_data = input_data.reshape(1, -1, 1)

            try:
                base_value = explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
                final_prediction = explainer.model(input_data).numpy().flatten()[0]
            except Exception as e:
                 logger.warning(f"Could not get base/final values for DeepExplainer: {e}")

            raw_shap_values = explainer.shap_values(input_data)

        # Pass all values to the formatter
        formatted_results = self._format_shap_values(
            raw_shap_values, 
            input_feature_names,
            original_values_dict, # <-- FIX: Pass the values
            top_k,
            base_value,
            final_prediction
        )
        
        return {"method": method, **formatted_results}