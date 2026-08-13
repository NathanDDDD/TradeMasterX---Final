from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_channel_id: str

    exchange: str = "binance"
    trading_pairs: str = "BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT"
    timeframes: str = "1h,4h"
    scan_interval_minutes: int = 5
    min_confluence: int = 2
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def pairs_list(self) -> list[str]:
        return [p.strip() for p in self.trading_pairs.split(",") if p.strip()]

    @property
    def timeframes_list(self) -> list[str]:
        return [t.strip() for t in self.timeframes.split(",") if t.strip()]


settings = Settings()
