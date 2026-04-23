# src/sentinalCloud-backend/app/routes/explainability_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

try:
    from app.utils.shap_explain import ShapExplainerService
except ImportError:
    logging.error("Could not import ShapExplainerService.")
    ShapExplainerService = None

router = APIRouter(prefix="/explain", tags=["Explainability"])
logger = logging.getLogger(__name__)

# --- Dependency Injection for SHAP Service ---
def get_shap_service(request: Request) -> ShapExplainerService:
    if ShapExplainerService is None:
        raise HTTPException(status_code=501, detail="SHAP service module could not be imported.")

    service = getattr(request.app.state, 'shap_service', None)
    if not service:
         logger.error("SHAP service not available in app state (wasn't loaded in main.py).")
         raise HTTPException(status_code=503, detail="SHAP Explainer service is not initialized or failed to load.")
    return service

# --- GET Endpoint for Explanations ---
@router.get("/{event_id}")
async def get_real_explanation_for_event_id(
    event_id: str,
    request: Request, # To get app state
    shap_service: ShapExplainerService = Depends(get_shap_service)
):
    """
    Looks up a real event_id from the cache, retrieves its data,
    and generates a real SHAP explanation.
    """
    # --- ADD THIS LINE BACK ---
    logger.info(f"--- !!! EXPLAIN ROUTE HANDLER REACHED for event_id: {event_id} !!! ---")
    # --- END ADD ---

    logger.info(f"Received REAL explanation request for event_id: {event_id}") # Original log

    # --- 1. Get Event Cache ---
    event_cache = getattr(request.app.state, 'event_cache', None)
    if event_cache is None:
        logger.error("Event cache not found in app state.")
        raise HTTPException(status_code=503, detail="Event cache is not available.")

    # --- 2. Look up Event ---
    event_data = event_cache.get(event_id)
    if not event_data:
        logger.warning(f"Event_id '{event_id}' not found in cache.")
        raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found. It may have expired or never existed.")

    try:
        # --- 3. Retrieve Stored Data ---
        processed_data_np = event_data.get("processed_data_np")
        model_key = event_data.get("model_key")

        if processed_data_np is None or model_key is None:
            logger.error(f"Cached data for event '{event_id}' is incomplete.")
            raise HTTPException(status_code=404, detail="Cached data for this event is corrupt or incomplete.")

        # --- 4. Reconstruct DataFrame for SHAP Service ---
        # Get feature names from the shap_service (loaded during startup)
        feature_names = shap_service.background_data_columns

        if processed_data_np.shape[1] != len(feature_names):
            logger.error(f"Data mismatch for event '{event_id}'. Processed data has {processed_data_np.shape[1]} features, but SHAP background has {len(feature_names)}.")
            raise HTTPException(status_code=500, detail="Internal server error: Mismatch in feature count for explanation.")

        # Create the 2D DataFrame that explain_sample expects
        sample_df = pd.DataFrame(processed_data_np, columns=feature_names)

        # --- 5. Run REAL Explanation ---
        logger.info(f"Running shap_service.explain_sample for model '{model_key}'...")
        explanation = shap_service.explain_sample(
            sample_df=sample_df,
            model_name=model_key,
            top_k=7 # Get top 7 features
        )

        # --- 6. Return Result ---
        logger.info(f"Successfully generated SHAP explanation for event: {event_id}")
        return {
            "event_id": event_id,
            "model_used": model_key,
            "shap_explanation": explanation # This is the real result from shap_explain.py
        }

    except HTTPException as http_exc: # Re-raise HTTP exceptions directly
        raise http_exc
    except Exception as e:
        logger.error(f"Error generating REAL explanation for {event_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {e}")