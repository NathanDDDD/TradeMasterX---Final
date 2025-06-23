import json
import os
from trademasterx.utils.logger import get_logger

class Memory:
    """Simple persistent memory for storing signals, trades, or state."""
    def __init__(self, memory_path='memory.json'):
        self.memory_path = memory_path
        self.logger = get_logger("Memory")
        self.data = self.load()

    def load(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.memory_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        self.logger.info(f"Memory saved to {self.memory_path}")

    def log_signal(self, signal):
        self.data.setdefault('signals', []).append(signal)
        self.save()

    def log_trade(self, trade):
        self.data.setdefault('trades', []).append(trade)
        self.save()

class LayeredMemory:
    """Layered memory for storing context/history (FinMem-inspired)."""
    def __init__(self):
        self.layers = []

    def add(self, info):
        self.layers.append(info)

    def get_recent(self, n=5):
        return self.layers[-n:] 