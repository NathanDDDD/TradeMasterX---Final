import yaml
import os

class Config:
    """Loads and stores configuration from a YAML file."""
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.data = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            # Provide a default config if file does not exist
            return {
                'trading': {
                    'risk': 0.01,
                    'symbols': ['BTCUSDT'],
                    'timeframe': '1h',
                },
                'logging': {
                    'level': 'INFO'
                }
            }
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        return self.data.get(key, default) 