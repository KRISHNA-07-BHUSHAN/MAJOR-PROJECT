"""
This service manages the state for attack simulations.

It provides a thread-safe class for sequential static simulations and a
function for generating dynamic, randomized attack data.
"""
import random
from threading import Lock
from typing import Dict, Any, List

# A predefined list of attack vectors to simulate a sequential attack
MOCK_ATTACK_VECTORS: List[Dict[str, Any]] = [
    {"flow_duration": 11264219, "tot_fwd_pkts": 40, "tot_bwd_pkts": 0, "totlen_fwd_pkts": 0, "type": "Port Scan"},
    {"flow_duration": 4, "tot_fwd_pkts": 2, "tot_bwd_pkts": 0, "totlen_fwd_pkts": 2944, "type": "DDoS"},
    {"flow_duration": 5000000, "tot_fwd_pkts": 8, "tot_bwd_pkts": 4, "totlen_fwd_pkts": 1024, "type": "Botnet C&C"},
    {"flow_duration": 200, "tot_fwd_pkts": 2, "tot_bwd_pkts": 2, "totlen_fwd_pkts": 80, "type": "SQL Injection Probe"},
]

class StaticSimulator:
    """A thread-safe class to manage the state of a static simulation.
    
    This prevents race conditions when multiple server workers access the
    simulation index at the same time.
    """
    def __init__(self, vectors: List[Dict[str, Any]]):
        self.vectors = vectors
        self.index = 0
        self.lock = Lock() # Ensures only one thread can modify the index at a time

    def get_next_vector(self) -> Dict[str, Any]:
        """Atomically retrieves the next vector and advances the index."""
        with self.lock:
            # If we've reached the end of the list, loop back to the beginning
            if self.index >= len(self.vectors):
                self.index = 0
            
            vector = self.vectors[self.index]
            self.index += 1
            return vector

# Create a single instance (singleton) to be imported and used across the application.
# This ensures all requests share the same simulation state.
static_simulator = StaticSimulator(MOCK_ATTACK_VECTORS)

def generate_dynamic_vector() -> Dict[str, Any]:
    """Generates a new, dynamically created mock attack vector."""
    return {
        "flow_duration": random.randint(1000, 15000000),
        "tot_fwd_pkts": random.randint(20, 200),
        "tot_bwd_pkts": random.randint(0, 50),
        "totlen_fwd_pkts": random.randint(1000, 50000),
        "type": random.choice(['Generated DDoS', 'Generated Port Flood'])
    }