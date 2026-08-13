import asyncio
import logging
from datetime import datetime, timezone

from config.settings import settings
from signals.data_fetcher import DataFetcher
from signals.strategies import evaluate
from signals.models import Signal
from telegram_bot.formatter import format_signal, format_daily_recap
from telegram_bot.publisher import TelegramPublisher

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("TradeMasterX")

daily_signals: list[Signal] = []


async def scan_once(fetcher: DataFetcher, publisher: TelegramPublisher) -> None:
    logger.info("Starting scan cycle...")
    for pair in settings.pairs_list:
        for timeframe in settings.timeframes_list:
            df = await fetcher.fetch_ohlcv(pair, timeframe)
            if df.empty:
                continue

            signal = evaluate(df, pair, timeframe, settings.min_confluence)
            if signal:
                logger.info(f"Signal: {signal.direction.value} {signal.pair} ({timeframe})")
                msg = format_signal(signal)
                await publisher.send(msg)
                daily_signals.append(signal)

    logger.info("Scan cycle complete.")


async def send_daily_recap(publisher: TelegramPublisher) -> None:
    global daily_signals
    msg = format_daily_recap(daily_signals)
    await publisher.send(msg)
    daily_signals = []
    logger.info("Daily recap sent, signal list cleared.")


async def main() -> None:
    logger.info("TradeMasterX Signals starting...")
    logger.info(f"Exchange: {settings.exchange}")
    logger.info(f"Pairs: {settings.pairs_list}")
    logger.info(f"Timeframes: {settings.timeframes_list}")
    logger.info(f"Scan interval: {settings.scan_interval_minutes}m")
    logger.info(f"Min confluence: {settings.min_confluence}")

    fetcher = DataFetcher(settings.exchange)
    publisher = TelegramPublisher(settings.telegram_bot_token, settings.telegram_channel_id)

    last_recap_date = None
    interval_seconds = settings.scan_interval_minutes * 60

    while True:
        try:
            await scan_once(fetcher, publisher)
        except Exception as e:
            logger.error(f"Scan failed: {e}")

        now = datetime.now(timezone.utc)
        if last_recap_date != now.date() and now.hour >= 23 and now.minute >= 55:
            try:
                await send_daily_recap(publisher)
                last_recap_date = now.date()
            except Exception as e:
                logger.error(f"Daily recap failed: {e}")

        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
