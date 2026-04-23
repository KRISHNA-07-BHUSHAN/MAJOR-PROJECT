# src/sentinalCloud-backend/app/main.py (Complete Final Version)
"""
Main application file for the SentinelCloud FastAPI backend.
Initializes the app, manages service lifecycles, configures CORS,
and includes API routers with correct prefixes directly under the app.
Uses an explicit map to link datasets and models.
"""
import logging
import random # <-- MAKE SURE THIS IS IMPORTED
from contextlib import asynccontextmanager
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, Request, HTTPException # <-- MAKE SURE HTTPException IS IMPORTED
from fastapi.middleware.cors import CORSMiddleware

# --- Import Application Modules ---
from app.models import model_loader 
from app.utils.preprocessing import DataPreprocessor
from app.utils.shap_explain import ShapExplainerService 
from app.routes import (
    alerts_routes,
    detection_routes,
    explainability_routes,
    simulation_routes, 
    stats_routes
)
# --- 1. IMPORT YOUR NEW DYNAMIC SIMULATOR ---
from app.utils.dynamic_attack import DynamicAttackSimulator 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ... (Keep your DATASET_MODEL_MAP and map_loaded_models function exactly as they are) ...
# --- DEFINE DATASET & MODEL MAPPING HERE ---
DATASET_MODEL_MAP = [
    {
        "key": "CICIDS2017", 
        "name": "CICIDS 2017",
        "sample_files": ["CICIDS2017_V2_full_preprocessed_sample.csv"], 
        "model_file": "CICIDS_2017_V2.h5"
    },
    {
        "key": "NSLKDD",
        "name": "NSL-KDD",
        "sample_files": ["NSL_KDD_Preprocessed_sample.csv"], 
        "model_file": "NSL_KDD.h5"
    },
    {
        "key": "TONIOT", 
        "name": "ToN-IoT",
        "sample_files": [
            "TON_IOT_Firsthalf_sample.csv",
            "TON_IOT_Firsthalf_sample.npz",
            "TON_IOT_Secondhalf_sample.csv",
            "TON_IOT_Secondhalf_sample.npz"
        ],
        "model_file": "TON_IOT.h5"
    },
]
# --- End Mapping Definition ---

# --- Helper to map loaded lists to dicts ---
def map_loaded_models(map_config, loaded_models_list, model_infos_list):
    # ... (This function is unchanged) ...
    models_dict = {}
    model_infos_dict = {}
    loaded_model_names = {info.get("name"): idx for idx, info in enumerate(model_infos_list)}
    loaded_model_paths = {Path(info.get("path")).name: idx for idx, info in enumerate(model_infos_list)}

    logger.info(f"Attempting to map loaded models using keys: {list(item['key'] for item in map_config)}")
    logger.info(f"Loaded model names found by loader: {list(loaded_model_names.keys())}")
    logger.info(f"Loaded model filenames found by loader: {list(loaded_model_paths.keys())}")

    for item in map_config:
        map_key = item['key']
        model_filename = item['model_file']
        model_name_stem = Path(model_filename).stem 

        found_idx = None
        if model_name_stem in loaded_model_names:
            found_idx = loaded_model_names[model_name_stem]
            logger.info(f"Matched map key '{map_key}' to loaded model name '{model_name_stem}'")
        elif model_filename in loaded_model_paths:
             found_idx = loaded_model_paths[model_filename]
             logger.info(f"Matched map key '{map_key}' to loaded model filename '{model_filename}'")

        if found_idx is not None and found_idx < len(loaded_models_list):
            models_dict[map_key] = loaded_models_list[found_idx]
            model_infos_dict[map_key] = model_infos_list[found_idx]
            model_infos_dict[map_key]['map_key'] = map_key
            logger.info(f"Successfully mapped key '{map_key}'")
        else:
            logger.error(f"Could not find a loaded model corresponding to map entry: Key='{map_key}', File='{model_filename}'")

    return models_dict, model_infos_dict
# --- End Helper ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Manages startup (model loading) and shutdown events using the defined map. """
    logger.info("--- Starting SentinelCloud API ---")
    app.state.dataset_map = DATASET_MODEL_MAP 

    # 1. Load ML models (Unchanged)
    models_dir_path = "./saved_models"
    try:
        from app.config import settings
        models_dir_path = getattr(settings, 'MODELS_DIR', models_dir_path)
        if models_dir_path != "./saved_models":
            logger.info(f"Loaded MODELS_DIR from settings: {models_dir_path}")
    except (ImportError, AttributeError):
        logger.warning(f"app.config.settings not found or MODELS_DIR not set, using default '{models_dir_path}'")
    
    logger.info(f"Loading models from directory: {models_dir_path}")
    try:
        loaded_models_list, model_infos_list = model_loader.load_models(models_dir=models_dir_path)
        models_dict, model_infos_dict = map_loaded_models(DATASET_MODEL_MAP, loaded_models_list, model_infos_list)
        if not models_dict: logger.warning("No models were successfully mapped after loading. Check map keys and filenames.")
        app.state.models = models_dict
        app.state.model_infos = model_infos_dict
    except Exception as load_err:
       logger.error(f"CRITICAL: Failed during model loading or mapping: {load_err}", exc_info=True)
       app.state.models = {}
       app.state.model_infos = {}

    # 2. Initialize DataPreprocessor (Unchanged)
    app.state.preprocessor = DataPreprocessor()
    logger.info("Data preprocessor initialized (no-scaling).")

    # 3. Initialize SHAP Explainer Service (Unchanged)
    try:
        # ... (all your existing SHAP loading code is unchanged) ...
        shap_bg_info = next((item for item in DATASET_MODEL_MAP if item['key'] == "NSLKDD"), None)
        if not shap_bg_info: raise FileNotFoundError("NSLKDD entry not found in map for SHAP background.")
        if not shap_bg_info.get('sample_files'): raise FileNotFoundError("NSLKDD entry in map missing 'sample_files' list.")
        background_data_filename = "NSL_KDD_Preprocessed_sample.csv"
        background_data_path = Path("app/data") / background_data_filename
        if not background_data_path.exists():
            logger.error(f"CRITICAL: SHAP background file not found at: {background_data_path}. Explainability API will fail.")
            app.state.shap_service = None
        else:
            logger.info(f"Loading SHAP background data from: {background_data_path.name}")
            background_df = pd.read_csv(background_data_path)
            n_rows_to_sample = min(100, len(background_df))
            if n_rows_to_sample > 0:
                background_df_sample = background_df.sample(n=n_rows_to_sample, random_state=42)
                if app.state.models:
                    models_list_for_shap = list(app.state.models.values())
                    model_names_for_shap = list(app.state.models.keys())
                    app.state.shap_service = ShapExplainerService(
                        models_list_for_shap, 
                        model_names_for_shap, 
                        background_df_sample
                    )
                    logger.info("✅ SHAP Explainer service initialized.")
                else:
                    logger.error("Skipping SHAP initialization because no models were loaded/mapped.")
                    app.state.shap_service = None
            else:
               logger.warning("SHAP background CSV seems empty, cannot create sample.")
               app.state.shap_service = None
    except Exception as e:
        logger.error(f"CRITICAL: Failed to initialize SHAP Explainer: {e}", exc_info=True)
        app.state.shap_service = None

    # 4. Initialize Event Cache (Unchanged)
    app.state.event_cache = {}
    logger.info("In-memory event cache initialized.")

    # --- 2. INITIALIZE YOUR DYNAMIC SIMULATOR ---
    app.state.dynamic_simulator = DynamicAttackSimulator(app)
    logger.info("✅ Dynamic Attack Simulator initialized.")
    # --- END OF CHANGE ---

    yield
    logger.info("--- Shutting down SentinelCloud API ---")

# ... (Keep app = FastAPI(...) and app.add_middleware(CORSMiddleware, ...) as is) ...
# --- FastAPI App Initialization ---
APP_TITLE = "SentinelCloud API"
APP_VERSION = "0.1.0"
try:
    from app.config import settings
    APP_TITLE = getattr(settings, 'APP_NAME', APP_TITLE)
    APP_VERSION = getattr(settings, 'APP_VERSION', APP_VERSION)
except (ImportError, AttributeError):
    pass

app = FastAPI(
    title=APP_TITLE, version=APP_VERSION,
    description="API for the SentinelCloud Intrusion Detection System.",
    lifespan=lifespan
)
# --- CORS Configuration ---
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# --- API Routers (Include directly with prefixes) ---
app.include_router(stats_routes.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(alerts_routes.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(detection_routes.router, prefix="/api/detect", tags=["Detection"])
app.include_router(explainability_routes.router, prefix="/api/explain", tags=["Explainability"])
app.include_router(simulation_routes.router, prefix="/api/simulation", tags=["Simulation"])


# --- 3. ADD THE NEW 'PULL' ENDPOINT ---
@app.post("/api/simulation/dynamic")
async def get_dynamic_simulation_event(request: Request):
    """
    Generates a single synthetic event using the DynamicAttackSimulator.
    This works just like the /static endpoint, providing one event on demand.
    """
    simulator = getattr(request.app.state, 'dynamic_simulator', None)
    if not simulator:
        logger.error("Dynamic Simulator not found in app.state.")
        raise HTTPException(status_code=503, detail="Dynamic Simulator is not initialized.")
    
    try:
        # 1. Choose a random model/dataset to generate for
        model_key_map = {"NSL": "NSLKDD", "CIC": "CICIDS2017", "TON": "TONIOT"}
        choice = random.choice(list(model_key_map.keys())) # "NSL", "CIC", or "TON"
        model_key = model_key_map[choice]

        # 2. Use your script's generator to get the raw features
        # This calls the _synthesize_sample method from your Python file
        features_dict = simulator._synthesize_sample(choice)

        # 3. Return the event in the *exact same format* as your static endpoint
        return {
            "data": features_dict,
            "label": "Unknown (Dynamic)", # The *true* label is unknown; the model will predict
            "model_key": model_key,
            "source": f"Dynamic Generator ({choice})"
        }
    except Exception as e:
        logger.error(f"Error in dynamic event generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating dynamic event: {e}")
# --- END OF NEW ENDPOINT ---


# --- Root Endpoint (Unchanged) ---
@app.get("/", tags=["Root"])
async def read_root(request: Request):
    # ... (This function is unchanged) ...
    shap_status = "loaded" if getattr(request.app.state, 'shap_service', None) else "NOT LOADED"
    model_count = len(getattr(request.app.state, 'models', {}))
    model_status = f"{model_count} models loaded" if model_count > 0 else "NO MODELS LOADED"
    preprocessor_status = "loaded (no-scaling)" if getattr(request.app.state, 'preprocessor', None) else "not loaded"
    cache_status = "loaded" if getattr(request.app.state, 'event_cache', None) is not None else "NOT LOADED"
    
    return {
        "message": f"Welcome to the {APP_TITLE}!",
        "version": APP_VERSION,
        "docs_url": "/docs",
        "status": {
            "models": model_status,
            "preprocessor": preprocessor_status,
            "shap_explainer": shap_status,
            "event_cache": cache_status
        }
    }