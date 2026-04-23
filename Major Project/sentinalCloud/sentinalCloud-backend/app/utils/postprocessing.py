"""
Post-processing utilities for enriching raw model predictions with
additional context, such as severity levels.
"""
from typing import Dict, List, Any

def _calculate_severity(probability: float) -> str:
    """Calculates a severity string based on a probability score."""
    if probability >= 0.9:
        return "high"
    if probability >= 0.7:
        return "medium"
    if probability >= 0.5:
        return "low"
    return "info"

def enrich_prediction_results(prediction_dict: Dict, meta: Dict = None) -> Dict:
    """
    Enriches the raw dictionary from `predict_ensemble` to conform to the
    `EnrichedPredictionResponse` schema.

    Args:
        prediction_dict: The raw output from `predict_ensemble`.
        meta: Optional metadata to include with each sample.

    Returns:
        A dictionary that can be validated by the `EnrichedPredictionResponse` Pydantic model.
    """
    enriched_samples = []
    model_names = prediction_dict.get("model_names", [])
    
    # Iterate safely over the lists in the prediction dictionary
    for i, avg_prob in enumerate(prediction_dict.get("avg_prob", [])):
        try:
            per_model_list = prediction_dict["per_model_probs"][i]
            
            enriched_samples.append({
                "index": i,
                "label": prediction_dict["labels"][i],
                "attack_probability": float(avg_prob),
                "severity": _calculate_severity(avg_prob),
                # Create a clean dictionary mapping model names to their probabilities
                "per_model_probs": {
                    name: float(prob) for name, prob in zip(model_names, per_model_list)
                },
                "meta": meta
            })
        except (IndexError, KeyError):
            # Skip this sample if data is malformed
            continue

    summary = {
        "n_samples": len(prediction_dict.get("avg_prob", [])),
        "n_models": prediction_dict.get("n_models", 0)
    }
    
    return {"summary": summary, "samples": enriched_samples}