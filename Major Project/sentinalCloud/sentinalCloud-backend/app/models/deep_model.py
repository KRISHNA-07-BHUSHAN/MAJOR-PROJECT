# sentinalCloud-backend/app/models/deep_model.py (Refactored for Future Use)
"""
Ensemble/Detection logic for running multiple Keras models.
NOTE: This file is NOT directly used by the current /api/detect endpoint,
      which uses predict.py for single model prediction.
      Keep this file if you plan to implement an ensemble endpoint later.
"""
import logging
from typing import List, Dict, Tuple, Any, Optional # Added Optional

import numpy as np
from tensorflow.keras.models import Model # Keep Model import

# --- REMOVED global model loading ---
# MODELS, MODEL_INFOS = load_models()
# Model loading should happen ONLY in main.py lifespan

logger = logging.getLogger(__name__)

# Default threshold if not passed (consider moving to config)
DEFAULT_DETECTION_THRESHOLD = 0.5


def _ensure_correct_dimensions(model: Model, X: np.ndarray) -> np.ndarray:
    """
    Adjusts the input array `X` dimensions to match the model's expected input shape.
    Handles common 2D -> 3D and 3D -> 2D adjustments based on model.input_shape.
    Assumes X has the batch dimension already (e.g., shape (1, num_features)).
    """
    model_input_shape = model.input_shape # e.g., (None, steps, features_per_step) or (None, features)
    if isinstance(model_input_shape, list):
        # Handle models with multiple inputs if necessary (taking first for now)
        logger.warning("Model has multiple inputs, using shape of the first one for dimension check.")
        model_input_shape = model_input_shape[0]

    # --- Refined Dimension Handling ---
    # Case 1: Model expects 3D (e.g., LSTM/Conv1D: (None, steps, features_per_step)), input is 2D (batch, features)
    if len(model_input_shape) == 3 and X.ndim == 2:
        expected_steps = model_input_shape[1]
        expected_feats_per_step = model_input_shape[2]
        num_features_in = X.shape[1]
        logger.debug(f"Model expects 3D (~{model_input_shape}), input is 2D ({X.shape}). Attempting reshape.")

        # Try common reshape patterns (adjust based on your actual model needs)
        # Pattern A: (batch, features) -> (batch, features, 1) if steps=features, feats_per_step=1
        if expected_steps == num_features_in and expected_feats_per_step == 1:
            X = X.reshape(X.shape[0], expected_steps, 1)
            logger.debug(f"Reshaped input to {X.shape} for (None, N, 1) model.")
        # Pattern B: (batch, features=steps*feats_per_step) -> (batch, steps, feats_per_step)
        elif expected_steps is not None and expected_feats_per_step is not None and expected_steps * expected_feats_per_step == num_features_in:
            X = X.reshape(X.shape[0], expected_steps, expected_feats_per_step)
            logger.debug(f"Reshaped input to {X.shape} for (None, N, M) model.")
        else:
            logger.warning(f"Cannot automatically reshape 2D input ({X.shape}) to match model's expected 3D shape {model_input_shape}. Using original.")
            # Consider raising an error here if reshape is mandatory

    # Case 2: Model expects 2D (e.g., Dense: (None, features)), input is 3D (maybe from preprocessor?)
    elif len(model_input_shape) == 2 and X.ndim == 3:
        logger.warning(f"Model expects 2D ({model_input_shape}), but input is 3D ({X.shape}). Attempting squeeze/reshape.")
        # Try squeezing if middle dim is 1: (batch, 1, features) -> (batch, features)
        if X.shape[1] == 1:
            X = np.squeeze(X, axis=1)
            logger.debug(f"Squeezed input to {X.shape}.")
        # Add other potential reshapes if needed
        else:
             logger.error(f"Cannot automatically reshape 3D input ({X.shape}) to match model's expected 2D shape {model_input_shape}.")
             raise ValueError("Input dimension mismatch for 2D model.") # Raise error if reshape fails

    # Ensure correct dtype
    return X.astype(np.float32)


def _get_attack_probability(preds: np.ndarray) -> np.ndarray:
    """
    Extracts the attack probability from raw model predictions.
    Assumes binary classification. Adjust if multi-class.
    Handles different output shapes.
    """
    if not isinstance(preds, np.ndarray):
        logger.error(f"Prediction result is not a numpy array: {type(preds)}")
        # Return a default value or raise error depending on desired behavior
        # Returning array of 0s with same batch size if possible
        return np.zeros(preds.shape[0] if hasattr(preds, 'shape') and len(preds.shape)>0 else 1)


    logger.debug(f"Processing raw prediction shape: {preds.shape}")
    # Case 1: Output shape (batch_size, 1), sigmoid activation -> Value is attack prob
    if preds.ndim == 2 and preds.shape[1] == 1:
        probs = np.squeeze(preds, axis=1)
    # Case 2: Output shape (batch_size, 2), softmax activation -> Prob is in index 1 (assuming index 1 = Attack)
    elif preds.ndim == 2 and preds.shape[1] == 2:
        probs = preds[:, 1]
    # Case 3: Output shape (batch_size,) -> Assume value is attack prob directly
    elif preds.ndim == 1:
        probs = preds
    # Add other cases or error handling if necessary
    else:
        logger.warning(f"Unexpected prediction output shape {preds.shape}. Attempting to squeeze.")
        try:
             probs = np.squeeze(preds)
             # If still not 1D, something is wrong
             if probs.ndim != 1:
                  logger.error(f"Could not reduce prediction {preds.shape} to 1D probabilities.")
                  probs = np.zeros(preds.shape[0]) # Default to 0
        except Exception as e:
             logger.error(f"Error squeezing prediction {preds.shape}: {e}")
             probs = np.zeros(preds.shape[0]) # Default to 0

    # Ensure probabilities are clipped between 0 and 1
    return np.clip(probs, 0.0, 1.0)


def predict_ensemble(
    X: np.ndarray,
    # --- MODIFIED: Accept models and infos as arguments ---
    models: Dict[str, Model],
    model_infos: Dict[str, Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None, # Allow weighting by model key
    threshold: float = DEFAULT_DETECTION_THRESHOLD
) -> dict:
    """
    Runs specified models on input X, performs a weighted soft vote, and returns results.
    The models and their info are passed as arguments.

    Args:
        X: Preprocessed input data (NumPy array, samples x features).
        models: Dictionary mapping model keys (e.g., 'CICIDS2017') to loaded Keras models.
        model_infos: Dictionary mapping model keys to their metadata (like 'input_shape').
        weights: Optional dictionary mapping model keys to voting weights. If None, equal weight.
        threshold: Probability threshold to classify as 'attack'.

    Returns:
        Dictionary containing ensemble prediction results.
    """
    if not models or not model_infos:
        logger.error("No models or model_infos provided to predict_ensemble.")
        raise ValueError("Models and model_infos dictionaries are required.")

    model_keys = list(models.keys()) # Use keys from the passed dict
    n_models = len(model_keys)
    batch_size = X.shape[0]
    per_model_probs = np.zeros((batch_size, n_models), dtype=float)

    logger.info(f"Running ensemble prediction with models: {model_keys}")

    for i, key in enumerate(model_keys):
        model = models[key]
        model_info = model_infos.get(key, {}) # Get info safely
        try:
            # Reshape input specifically for this model
            input_data = _ensure_correct_dimensions(model, X)
            # Predict using the specific model
            raw_preds = model.predict(input_data, batch_size=min(batch_size, 32), verbose=0) # Add batch_size
            # Extract attack probability
            attack_prob = _get_attack_probability(raw_preds)
            per_model_probs[:, i] = attack_prob
            # logger.debug(f"Model '{key}' predicted probs (first 5): {attack_prob[:5]}")

        except Exception as e:
            logger.error(f"Prediction failed for model '{key}'. Defaulting to 0. Error: {e}", exc_info=True)
            per_model_probs[:, i] = 0.0 # Assign 0 probability on error

    # Determine weights
    if weights:
         # Use weights based on keys, default to 0 if key missing in weights dict
         model_weights_list = [weights.get(key, 0.0) for key in model_keys]
         model_weights = np.array(model_weights_list, dtype=float)
         # Normalize weights
         sum_weights = model_weights.sum()
         if sum_weights > 0:
             model_weights /= sum_weights
         else:
              logger.warning("Sum of provided weights is zero. Using equal weights.")
              model_weights = np.ones(n_models) / n_models # Fallback to equal
    else:
        # Default to equal weights if none provided
        model_weights = np.ones(n_models) / n_models

    logger.debug(f"Using model weights: {dict(zip(model_keys, model_weights))}")

    # Calculate weighted average probability
    avg_prob = np.average(per_model_probs, axis=1, weights=model_weights)

    # Determine final labels based on threshold
    labels_idx = (avg_prob >= threshold).astype(int)
    labels = ["attack" if label_idx == 1 else "normal" for label_idx in labels_idx]

    # Return structured results
    return {
        "n_models_used": n_models,
        "model_keys": model_keys,
        "model_weights": model_weights.tolist(), # Include weights used
        "per_model_probs": per_model_probs.tolist(),
        "avg_prob": avg_prob.tolist(),
        "threshold": threshold, # Include threshold used
        "labels_idx": labels_idx.tolist(),
        "labels": labels,
    }

# --- Optional: Add a single prediction function if needed for consistency ---
# (Similar to the one created in predict.py, but could live here if preferred)
# def predict_single(
#     X: np.ndarray,
#     model: Model,
#     threshold: float = DEFAULT_DETECTION_THRESHOLD
# ) -> dict :
#      """ Runs a single model prediction. """
#      input_data = _ensure_correct_dimensions(model, X)
#      raw_preds = model.predict(input_data, verbose=0)
#      attack_prob = _get_attack_probability(raw_preds)
#      # ... format single result ...
#      return { ... }