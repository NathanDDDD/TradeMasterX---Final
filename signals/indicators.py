import pandas as pd


def compute_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_macd(
    df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
) -> dict[str, pd.Series]:
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


def compute_ema(df: pd.DataFrame, window: int = 21) -> pd.Series:
    return df["close"].ewm(span=window, adjust=False).mean()


def compute_bollinger(
    df: pd.DataFrame, window: int = 20, std: int = 2
) -> dict[str, pd.Series]:
    middle = df["close"].rolling(window=window).mean()
    rolling_std = df["close"].rolling(window=window).std()
    upper = middle + (rolling_std * std)
    lower = middle - (rolling_std * std)
    return {"upper": upper, "middle": middle, "lower": lower}
