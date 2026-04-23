# app/utils/dynamic_label_mapper.py

"""
Mapping engine for dynamic attack labels.
Keeps static simulation fully untouched.
"""

# --- NSL-KDD ---
NSL_KDD_LABEL_MAP = {
    0: 'normal', 1: 'neptune', 2: 'smurf', 3: 'back', 4: 'pod', 5: 'teardrop',
    6: 'land', 7: 'ipsweep', 8: 'nmap', 9: 'satan', 10: 'guess_passwd',
    11: 'ftp_write', 12: 'multihop', 13: 'phf', 14: 'warezclient',
    15: 'warezmaster', 16: 'spy', 17: 'buffer_overflow', 18: 'loadmodule',
    19: 'perl', 20: 'rootkit', 21: 'xterm', 22: 'sqlattack'
}

# --- CICIDS2017 ---
CICIDS_LABEL_MAP = {
    0: 'BENIGN', 1: 'DoS Hulk', 2: 'DoS GoldenEye', 3: 'DoS Slowloris',
    4: 'DoS Slowhttptest', 5: 'DoS Heartbleed', 6: 'FTP-Patator',
    7: 'SSH-Patator', 8: 'Web Attack - Brute Force', 9: 'Web Attack - XSS',
    10: 'Web Attack - SQL Injection', 11: 'Infiltration', 12: 'Bot',
    13: 'DDoS', 14: 'PortScan', 15: 'Heartbleed'
}

# --- ToN-IoT (YOU CAN EDIT THIS ANYTIME) ---
# TON-IoT — REAL USER-PROVIDED LABELS
TONIOT_LABEL_MAP = {
    0: "normal",
    1: "ddos",
    2: "dos",
    3: "injection",
    4: "password",
    5: "scanning",
    6: "backdoor",
    7: "mitm",
    8: "ransomeware",
    9: "xss"
}
# You can extend mapping to 20 if needed.


def map_dynamic_label(model_key: str, raw_index: int) -> str:
    """
    Returns the correct attack name for dynamic attack.
    STATIC simulation is never touched.
    """
    if raw_index is None:
        return "Unknown"

    if model_key == "NSLKDD":
        return NSL_KDD_LABEL_MAP.get(raw_index, f"NSL_Class_{raw_index}")

    if model_key == "CICIDS2017":
        return CICIDS_LABEL_MAP.get(raw_index, f"CIC_Class_{raw_index}")

    if model_key == "TONIOT":
        return TONIOT_LABEL_MAP.get(raw_index, f"ToN_Class_{raw_index}")

    return f"Class_{raw_index}"
