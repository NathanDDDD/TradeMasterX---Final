import re
from signals.models import Signal, Direction


def _escape_md(text: str) -> str:
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", str(text))


def _format_price(price: float) -> str:
    if price >= 1:
        return f"{price:,.2f}"
    return f"{price:.8f}".rstrip("0").rstrip(".")


def format_signal(signal: Signal) -> str:
    direction_emoji = "\U0001F7E2" if signal.direction == Direction.LONG else "\U0001F534"
    direction_label = signal.direction.value

    tp_lines = []
    for i, (tp, pct) in enumerate(zip(signal.take_profits, signal.tp_percentages), 1):
        tp_lines.append(
            f"\U0001F3AF *TP{i}:* `{_escape_md(_format_price(tp))}` \\({_escape_md(str(pct))}%\\)"
        )

    strategies_str = _escape_md(" + ".join(signal.strategies))
    rr = _escape_md(str(signal.risk_reward_ratio))

    msg = (
        f"\U0001F514 *SIGNAL — {_escape_md(direction_label)}* {direction_emoji}\n"
        f"\n"
        f"*Pair:*      `{_escape_md(signal.pair)}`\n"
        f"*Entry:*     `{_escape_md(_format_price(signal.entry_low))}` — `{_escape_md(_format_price(signal.entry_high))}`\n"
        f"*Stop Loss:* `{_escape_md(_format_price(signal.stop_loss))}` ❌\n"
        f"\n"
        + "\n".join(tp_lines)
        + "\n"
        f"\n"
        f"*Timeframe:* `{_escape_md(signal.timeframe)}`\n"
        f"*Risk:*      `{_escape_md(str(signal.risk_percent))}%`\n"
        f"*R:R:*       `{rr}`\n"
        f"*Strategy:*  _{strategies_str}_\n"
        f"\n"
        f"— _TradeMasterX_"
    )
    return msg


def format_no_signals() -> str:
    return (
        "\U0001F50D *Scan Complete*\n"
        "\n"
        "No confluence signals detected this cycle\\.\n"
        "\n"
        "— _TradeMasterX_"
    )


def format_daily_recap(signals: list[Signal]) -> str:
    if not signals:
        return (
            "\U0001F4CA *Daily Recap*\n"
            "\n"
            "No signals were emitted today\\.\n"
            "\n"
            "— _TradeMasterX_"
        )

    longs = sum(1 for s in signals if s.direction == Direction.LONG)
    shorts = sum(1 for s in signals if s.direction == Direction.SHORT)
    pairs = set(s.pair for s in signals)

    lines = [
        "\U0001F4CA *Daily Recap*\n",
        f"*Signals:* `{_escape_md(str(len(signals)))}`",
        f"\U0001F7E2 Longs: `{_escape_md(str(longs))}` \\| \U0001F534 Shorts: `{_escape_md(str(shorts))}`",
        f"*Pairs:* `{_escape_md(', '.join(sorted(pairs)))}`\n",
    ]

    for s in signals:
        direction_emoji = "\U0001F7E2" if s.direction == Direction.LONG else "\U0001F534"
        lines.append(
            f"{direction_emoji} `{_escape_md(s.pair)}` {_escape_md(s.direction.value)} "
            f"@ `{_escape_md(_format_price(s.entry_low))}`"
        )

    lines.append(f"\n— _TradeMasterX_")
    return "\n".join(lines)
