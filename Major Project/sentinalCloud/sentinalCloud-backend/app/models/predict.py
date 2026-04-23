# src/sentinalCloud-backend/app/models/predict.py
"""
Contains functions for running model predictions.
"""
import numpy as np
from tensorflow.keras.models import Model # Import Model type hint
import logging
from typing import Tuple # Import Tuple for type hinting

logger = logging.getLogger(__name__)

def predict_single_model(model: Model, x_input: np.ndarray) -> Tuple[str, float]:
    """
    Runs prediction on a single, preprocessed, and correctly reshaped sample
    using the provided Keras model.

    Returns:
        A tuple of (prediction_label: str, confidence: float).
        - 'Normal' or 'Attack'
        - Confidence of the *predicted* class (0.0 to 1.0)
    """
    if not isinstance(model, Model):
         logger.error("Invalid model object passed to predict_single_model.")
         return "Error", 0.0
    if not isinstance(x_input, np.ndarray):
         logger.error("Invalid input type passed to predict_single_model. Expected NumPy array.")
         return "Error", 0.0

    try:
        # verbose=0 prevents TensorFlow from printing progress bars
        raw_preds = model.predict(x_input, verbose=0)
        # logger.debug(f"Raw prediction output shape: {raw_preds.shape}, values: {raw_preds}") # Original log

        prediction_label = "Normal" # Default
        confidence = 0.0

        # --- Process raw_preds based on model output shape ---

        # Case 1: Output shape (1, 1) (binary classification, sigmoid)
        if raw_preds.shape == (1, 1):
            confidence_raw = float(raw_preds[0, 0])
            if confidence_raw >= 0.5:
                prediction_label = "Attack"
                confidence = confidence_raw
            else:
                prediction_label = "Normal"
                confidence = 1.0 - confidence_raw # Confidence of being Normal

        # Case 2: Output shape (1, 2) (binary classification, softmax)
        elif raw_preds.shape == (1, 2):
            # Assumes index 0 is 'Normal', index 1 is 'Attack'
            confidence = float(np.max(raw_preds[0])) # Confidence of predicted class
            predicted_index = np.argmax(raw_preds[0])
            prediction_label = "Attack" if predicted_index == 1 else "Normal"

        # Case 3: Output shape (1,) (squeezed binary)
        elif raw_preds.shape == (1,):
             confidence_raw = float(raw_preds[0])
             if confidence_raw >= 0.5:
                 prediction_label = "Attack"; confidence = confidence_raw
             else:
                 prediction_label = "Normal"; confidence = 1.0 - confidence_raw

        # Case 4: Multi-class (e.g., (1, 16) as seen in logs)
        elif raw_preds.ndim == 2 and raw_preds.shape[0] == 1 and raw_preds.shape[1] > 2:
            num_classes = raw_preds.shape[1]
            logger.info(f"Interpreting multi-class output (shape 1, {num_classes})")
            # Get the index (0, 1, 2,...) of the highest probability
            predicted_index = np.argmax(raw_preds[0])
            # Get the probability (confidence) of that highest class
            confidence = float(np.max(raw_preds[0]))

            # --- NEW: Log the full probability array ---
            logger.info(f"  Full probabilities: {[f'{p:.4f}' for p in raw_preds[0]]}")
            # --- End New Log ---

            # --- ASSUMPTION: Index 0 is 'Normal', all others are 'Attack' ---
            prediction_label = "Normal" if predicted_index == 0 else "Attack"

        else:
             logger.error(f"Cannot interpret prediction shape: {raw_preds.shape}. Returning 'Error'.")
             return "Error", 0.0

        # Return the final label and its confidence
        # logger.info(f"Final prediction: {prediction_label}, Conf: {confidence:.4f}") # Moved to detection_routes
        return prediction_label, max(0.0, min(1.0, confidence))

    except Exception as e:
        logger.error(f"Error during model.predict: {e}", exc_info=True)
        return "Error", 0.0 # Return error state