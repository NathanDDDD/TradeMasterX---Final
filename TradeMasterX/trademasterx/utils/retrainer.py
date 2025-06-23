from trademasterx.utils.data_logger import DataLogger
from datetime import datetime, timedelta

class Retrainer:
    def __init__(self, logger: DataLogger, retrain_interval_trades=100, retrain_interval_hours=24):
        self.logger = logger
        self.retrain_interval_trades = retrain_interval_trades
        self.retrain_interval_hours = retrain_interval_hours
        self.last_retrain_time = datetime.now()
        self.trade_count = 0

    def record_trade(self):
        self.trade_count += 1
        if self.trade_count >= self.retrain_interval_trades or \
           datetime.now() - self.last_retrain_time > timedelta(hours=self.retrain_interval_hours):
            self.retrain()

    def retrain(self):
        # Placeholder: recalibrate thresholds, retrain models, etc.
        event = f"Retraining triggered at {datetime.now().isoformat()}"
        details = "Recalibrated indicator thresholds (stub)"
        self.logger.log_retraining(event, details)
        self.last_retrain_time = datetime.now()
        self.trade_count = 0 