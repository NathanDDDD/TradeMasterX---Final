import pandas as pd
import logging
from signals.indicators import compute_rsi, compute_macd, compute_ema, compute_bollinger
from signals.models import Signal, Direction

logger = logging.getLogger(__name__)


def _price_str(price: float) -> float:
    return round(price, 8)


def check_rsi_reversal(df: pd.DataFrame) -> str | None:
    rsi = compute_rsi(df)
    last_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2]

    if last_rsi < 30 and prev_rsi >= 30:
        return "LONG"
    if last_rsi > 70 and prev_rsi <= 70:
        return "SHORT"
    return None


def check_macd_cross(df: pd.DataFrame) -> str | None:
    macd_data = compute_macd(df)
    macd_line = macd_data["macd"]
    signal_line = macd_data["signal"]

    curr_macd = macd_line.iloc[-1]
    prev_macd = macd_line.iloc[-2]
    curr_signal = signal_line.iloc[-1]
    prev_signal = signal_line.iloc[-2]

    if prev_macd <= prev_signal and curr_macd > curr_signal:
        return "LONG"
    if prev_macd >= prev_signal and curr_macd < curr_signal:
        return "SHORT"
    return None


def check_ema_cross(df: pd.DataFrame) -> str | None:
    ema_fast = compute_ema(df, window=9)
    ema_slow = compute_ema(df, window=21)

    curr_fast, prev_fast = ema_fast.iloc[-1], ema_fast.iloc[-2]
    curr_slow, prev_slow = ema_slow.iloc[-1], ema_slow.iloc[-2]

    if prev_fast <= prev_slow and curr_fast > curr_slow:
        return "LONG"
    if prev_fast >= prev_slow and curr_fast < curr_slow:
        return "SHORT"
    return None


def check_bollinger_bounce(df: pd.DataFrame) -> str | None:
    bb = compute_bollinger(df)
    rsi = compute_rsi(df)

    close = df["close"].iloc[-1]
    lower = bb["lower"].iloc[-1]
    upper = bb["upper"].iloc[-1]
    last_rsi = rsi.iloc[-1]

    if close <= lower and last_rsi < 35:
        return "LONG"
    if close >= upper and last_rsi > 65:
        return "SHORT"
    return None


STRATEGIES = {
    "RSI Reversal": check_rsi_reversal,
    "MACD Cross": check_macd_cross,
    "EMA Cross (9/21)": check_ema_cross,
    "Bollinger Bounce": check_bollinger_bounce,
}


def evaluate(df: pd.DataFrame, pair: str, timeframe: str, min_confluence: int = 2) -> Signal | None:
    if df.empty or len(df) < 30:
        return None

    results: dict[str, str] = {}
    for name, strategy_fn in STRATEGIES.items():
        try:
            direction = strategy_fn(df)
            if direction:
                results[name] = direction
        except Exception as e:
            logger.warning(f"Strategy {name} failed for {pair}: {e}")

    if len(results) < min_confluence:
        return None

    long_count = sum(1 for d in results.values() if d == "LONG")
    short_count = sum(1 for d in results.values() if d == "SHORT")

    if long_count >= min_confluence:
        direction = Direction.LONG
    elif short_count >= min_confluence:
        direction = Direction.SHORT
    else:
        return None

    close = df["close"].iloc[-1]
    atr = _calculate_atr(df)

    if direction == Direction.LONG:
        entry_low = _price_str(close * 0.998)
        entry_high = _price_str(close * 1.002)
        stop_loss = _price_str(close - (atr * 1.5))
        take_profits = [
            _price_str(close + (atr * 1.5)),
            _price_str(close + (atr * 2.5)),
            _price_str(close + (atr * 4.0)),
        ]
    else:
        entry_low = _price_str(close * 0.998)
        entry_high = _price_str(close * 1.002)
        stop_loss = _price_str(close + (atr * 1.5))
        take_profits = [
            _price_str(close - (atr * 1.5)),
            _price_str(close - (atr * 2.5)),
            _price_str(close - (atr * 4.0)),
        ]

    matching_strategies = [name for name, d in results.items() if d == direction.value]

    return Signal(
        pair=pair,
        direction=direction,
        entry_low=entry_low,
        entry_high=entry_high,
        stop_loss=stop_loss,
        take_profits=take_profits,
        tp_percentages=[50, 30, 20],
        timeframe=timeframe,
        strategies=matching_strategies,
    )


def _calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().iloc[-1]
