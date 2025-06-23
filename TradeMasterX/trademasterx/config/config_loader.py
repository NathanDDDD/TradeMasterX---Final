def load_config():
    """Stub: Load config (extend for YAML/JSON/env)."""
    return {
        "symbols": ["BTCUSDT"],
        "trade_threshold": 0.7,
        "weights": {
            "pattern": 1.0,
            "indicator": 1.0,
            "sentiment": 1.0,
            "news": 1.0,
            "rl": 1.0
        }
    } 