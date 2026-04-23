"""
Provides functions to enrich raw attack data with context like
plausible attack types, reasons, and mitigation advice.
"""
from typing import Dict, List, Tuple

from app.schemas import FeatureRowSchema, AttackEnrichmentInfo

# This data remains the same - it's a good knowledge base.
ATTACK_DOCS = {
    "HTTP DDoS (Volumetric)": {
        "theory": "...",
        "mitigation": ["..."]
    },
    "SYN Flood (DDoS)": {
        "theory": "...",
        "mitigation": ["..."]
    },
    # ... (all your other attack docs)
    "Unknown Attack": {
        "theory": "Detected anomaly that doesn't match known heuristics. Investigate logs and packet captures.",
        "mitigation": ["Capture PCAP and inspect payloads...", "..."]
    }
}


def _get_heuristic_classification(row: FeatureRowSchema) -> Tuple[str, str]:
    """
    Internal function to determine attack type based on simple rules.
    Accepts a validated Pydantic model, making it type-safe.
    """
    # Simple rules using the validated data from the schema
    if row.dst_port in (80, 443) and row.packet_count > 1000 and row.duration < 10:
        return "HTTP DDoS (Volumetric)", "Large number of short-duration HTTP requests."
    if "syn" in row.tcp_flags.lower() and row.packet_count > 500:
        return "SYN Flood (DDoS)", "Many SYN packets without completing handshakes."
    if row.dst_port in (22, 3389) and row.src_bytes == 0 and row.dst_bytes > 0:
        return "Brute Force / Credential Attack", "Repeated connection attempts on remote login ports."
    if row.dst_port == 53 and row.packet_count > 500:
        return "DNS Amplification / DDoS", "Large number of DNS requests to single target."
    if row.packet_count > 200 and row.duration < 5:
        return "Generic DDoS/Scan", "High packet rate in short duration."
    
    return "Unknown Attack", "Pattern suggests anomaly but type is uncertain."


def get_attack_enrichment_info(feature_dict: Dict) -> AttackEnrichmentInfo:
    """
    Takes a dictionary of features, validates it, and returns a fully
    enriched object with attack context and mitigation advice.
    """
    # 1. Validate the raw dictionary into a structured Pydantic model
    validated_row = FeatureRowSchema(**feature_dict)

    # 2. Get the classification and reason from the heuristic logic
    attack_type, reason = _get_heuristic_classification(validated_row)

    # 3. Look up the documentation, with a safe fallback to "Unknown Attack"
    doc = ATTACK_DOCS.get(attack_type, ATTACK_DOCS["Unknown Attack"])

    # 4. Construct and return the final, structured Pydantic object
    return AttackEnrichmentInfo(
        attack_type=attack_type,
        reason=reason,
        theory=doc["theory"],
        mitigation_steps=doc["mitigation"]
    )