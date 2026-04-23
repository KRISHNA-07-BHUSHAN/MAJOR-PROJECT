"""
Discovers and loads all Keras/TensorFlow models from the specified models directory.
"""
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Any

from tensorflow.keras.models import load_model, Model

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = [".h5", ".keras", ".hdf5"]

def _find_model_paths(models_dir: Path) -> List[Path]:
    """
    Finds all supported model files and SavedModel directories within the models directory.
    
    Using pathlib is a more modern and object-oriented way to handle file paths.
    """
    if not models_dir.is_dir():
        return []

    # Find all files with supported extensions
    model_files = [p for ext in SUPPORTED_EXTS for p in models_dir.glob(f"*{ext}")]
    
    # Find all directories that look like TensorFlow SavedModels
    saved_model_dirs = [
        d for d in models_dir.iterdir() if d.is_dir() and (d / "saved_model.pb").exists()
    ]
    
    return sorted(model_files + saved_model_dirs)


def load_models(models_dir: str = settings.MODELS_DIR) -> Tuple[List[Model], List[Dict[str, Any]]]:
    """
    Loads all trained models from a directory into memory.

    This function is stateless. It finds, loads, and returns the models and their
    metadata without relying on global variables.

    Args:
        models_dir: The path to the directory containing model files.

    Returns:
        A tuple containing two parallel lists:
        - A list of the loaded Keras Model objects.
        - A list of dictionaries, each containing metadata for the corresponding model.
    """
    model_path = Path(models_dir)
    model_paths = _find_model_paths(model_path)
    
    loaded_models: List[Model] = []
    model_infos: List[Dict[str, Any]] = []

    if not model_paths:
        logger.warning(f"⚠️ No model files found in '{model_path}'. The detection endpoint will not work.")
        return [], []

    logger.info(f"Found {len(model_paths)} potential models. Attempting to load...")

    for path in model_paths:
        try:
            # Derives a clean name from the file/directory name
            model_name = path.stem if path.is_file() else path.name
            logger.info(f"🧠 Loading model: '{model_name}' from '{path}'")
            
            # compile=False is a performance optimization for inference-only models
            model = load_model(str(path), compile=False)
            
            loaded_models.append(model)
            model_infos.append({
                "path": str(path),
                "name": model_name,
                "input_shape": model.input_shape,
                "output_shape": model.output_shape,
            })
            logger.info(f"✅ Loaded '{model_name}' successfully. Input shape: {model.input_shape}")
        
        except Exception:
            logger.exception(f"❌ Failed to load model from '{path}'. It will be skipped.")

    logger.info(f"✅ Successfully loaded {len(loaded_models)} out of {len(model_paths)} models.")
    return loaded_models, model_infos