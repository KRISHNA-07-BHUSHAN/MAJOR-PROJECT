# sentinalCloud-backend/app/utils/preprocessing.py
import logging
from typing import Any, List, Union, Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# --- List of potential column names to drop ---
# Add any other label/target/index column names from your datasets here
KNOWN_LABEL_COLUMNS = [
    'Label', 
    'label', 
    
    'Attack Type',
    'Category',
    'Unnamed: 0',  # <-- THIS IS THE FIX
]

class DataPreprocessor:
    """
    Encapsulates logic for cleaning incoming data for inference.
    This version does NOT perform scaling but WILL drop known label columns.
    """
    def __init__(self):
        # No scaler is loaded or stored.
        logger.info("Preprocessor initialized in 'no-scaling' mode (will drop known label columns).")
        self.known_labels = KNOWN_LABEL_COLUMNS
        pass

    def _to_dataframe(self, data: Union[pd.DataFrame, np.ndarray, List[List[Any]], Dict[str, Any]]) -> pd.DataFrame:
        """Converts various input types to a DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data.copy()
        if isinstance(data, dict):
            # Handle single sample dict from detection_routes
            return pd.DataFrame([data])
        if isinstance(data, np.ndarray) or isinstance(data, list):
             # This path might not have column names, handle with care
             logger.warning("Preprocessing data from list or ndarray; label dropping might fail if columns unknown.")
             return pd.DataFrame(data)
        
        # Fallback for other unexpected types
        try:
             return pd.DataFrame(data)
        except Exception as e:
             logger.error(f"Could not convert input data to DataFrame: {e}")
             raise ValueError("Input data must be convertible to a Pandas DataFrame.")


    def transform(self, data: Union[pd.DataFrame, np.ndarray, List[List[Any]], Dict[str, Any]]) -> np.ndarray:
        """
        Cleans the input data, drops known label columns, 
        and returns a NumPy array.
        """
        df = self._to_dataframe(data)
        
        # --- Logic to Drop known label columns ---
        original_cols = df.columns.tolist()
        cols_to_drop = [col for col in original_cols if col in self.known_labels]
        
        if cols_to_drop:
            logger.info(f"Dropping label/metadata columns: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
        else:
            # This might happen if the input (e.g., from NPZ) only has features
            logger.info("No known label columns found to drop, processing all columns as features.")
        # --- End Logic ---

        # 1. Data Cleaning
        for col in df.columns:
            # pd.to_numeric handles columns that are already numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0.0, inplace=True) # Fill NaNs (from coerce or original)

        # 2. Convert to NumPy array
        processed_values = df.values.astype(np.float32)
        logger.info(f"Shape after dropping/cleaning (Samples, Features): {processed_values.shape}")
        
        return processed_values

    # --- THIS IS THE NEW FUNCTION YOU MUST ADD ---
    def transform_df(self, data: Union[pd.DataFrame, np.ndarray, List[List[Any]], Dict[str, Any]]) -> pd.DataFrame:
        """
        Cleans the input data, drops known label columns, 
        and returns a processed DataFrame *with* column names.
        This is for SHAP, to get the correct feature names.
        """
        df = self._to_dataframe(data)
        
        # --- Logic to Drop known label columns ---
        original_cols = df.columns.tolist()
        cols_to_drop = [col for col in original_cols if col in self.known_labels]
        
        if cols_to_drop:
            logger.info(f"[transform_df] Dropping label/metadata columns: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
        else:
            logger.info("[transform_df] No known label columns found to drop, processing all columns as features.")
        # --- End Logic ---

        # 1. Data Cleaning
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0.0, inplace=True) # Fill NaNs (from coerce or original)
        
        logger.info(f"[transform_df] Shape after dropping/cleaning (Samples, Features): {df.shape}")
        
        return df
    # --- END OF NEW FUNCTION ---