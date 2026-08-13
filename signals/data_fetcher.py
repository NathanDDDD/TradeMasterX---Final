import ccxt
import pandas as pd
import logging

logger = logging.getLogger(__name__)

OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


class DataFetcher:
    def __init__(self, exchange_id: str):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({"enableRateLimit": True})

    async def fetch_ohlcv(self, pair: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        try:
            ohlcv = self.exchange.fetch_ohlcv(pair, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=OHLCV_COLUMNS)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch {pair} {timeframe}: {e}")
            return pd.DataFrame()
