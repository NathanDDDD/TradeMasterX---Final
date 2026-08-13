from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class Direction(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Signal:
    pair: str
    direction: Direction
    entry_low: float
    entry_high: float
    stop_loss: float
    take_profits: list[float]
    tp_percentages: list[int]
    timeframe: str
    strategies: list[str]
    risk_percent: float = 2.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def risk_reward_ratio(self) -> float:
        entry_mid = (self.entry_low + self.entry_high) / 2
        risk = abs(entry_mid - self.stop_loss)
        if risk == 0:
            return 0.0
        reward = abs(self.take_profits[-1] - entry_mid) if self.take_profits else 0.0
        return round(reward / risk, 2)
