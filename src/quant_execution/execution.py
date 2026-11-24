"""Long-only execution rules for the frozen v5.4.1 research model."""

from dataclasses import dataclass
from math import isclose, isfinite


@dataclass(frozen=True)
class Bar:
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self):
        if not all(isfinite(price) and price > 0 for price in
                   (self.open, self.high, self.low, self.close)):
            raise ValueError("OHLC must be positive and finite")
        high = max(self.open, self.close, self.low)
        low = min(self.open, self.close, self.high)
        for name, observed, bound in (("high", self.high, high), ("low", self.low, low)):
            outside = observed < bound if name == "high" else observed > bound
            if outside:
                if not isclose(observed, bound, rel_tol=1e-12):
                    raise ValueError("Inconsistent OHLC")
                object.__setattr__(self, name, bound)

    def path(self, assumption):
        if assumption == "HL":
            return self.open, self.high, self.low, self.close
        if assumption == "LH":
            return self.open, self.low, self.high, self.close
        raise ValueError(f"Unknown OHLC path: {assumption}")


@dataclass(frozen=True)
class Order:
    kind: str
    reference: float
    stop: float
    target: float

    def __post_init__(self):
        if self.kind not in ("limit", "stop", "market"):
            raise ValueError(f"Unknown entry kind: {self.kind}")
        if not all(isfinite(price) for price in (self.stop, self.reference, self.target)):
            raise ValueError("Order levels must be finite")
        if not 0 < self.stop < self.reference < self.target:
            raise ValueError("Bracket levels must satisfy stop < reference < target")


@dataclass(frozen=True)
class Fill:
    side: str
    price: float
    fee_per_unit: float
    residual_slippage_per_unit: float

    @property
    def cash_per_unit(self):
        costs = self.fee_per_unit + self.residual_slippage_per_unit
        return self.price + costs if self.side == "buy" else self.price - costs


@dataclass(frozen=True)
class Costs:
    fee_bps: float
    slippage_bps: float

    def __post_init__(self):
        if not all(isfinite(bps) and 0 <= bps < 10_000 for bps in
                   (self.fee_bps, self.slippage_bps)):
            raise ValueError("Fees and slippage must be finite nonnegative bps below 10,000")

    def fill(self, raw, side, limit=None):
        if side not in ("buy", "sell"):
            raise ValueError(f"Unknown side: {side}")
        if not isfinite(raw) or raw <= 0:
            raise ValueError("Raw fill must be finite and positive")
        buying = side == "buy"
        slipped = raw * (1 + self.slippage_bps / 10_000 * (1 if buying else -1))
        if limit is None:
            price = slipped
        else:
            if not isfinite(limit) or limit <= 0:
                raise ValueError("Limit must be finite and positive")
            if (buying and raw > limit) or (not buying and raw < limit):
                raise ValueError("Limit not reached")
            price = min(slipped, limit) if buying else max(slipped, limit)
        # Model the remaining stress separately from the simulated execution price.
        return Fill(side, price, price * self.fee_bps / 10_000, abs(slipped - price))


def first_touch(path, level, *, upward):
    """Return only the part of the route on or after the first eligible touch."""
    opening = path[0]
    if (upward and opening >= level) or (not upward and opening <= level):
        return path
    for index in range(1, len(path)):
        prior, current = path[index - 1:index + 1]
        if (upward and prior < level <= current) or (not upward and prior > level >= current):
            return (level,) + path[index:]
    return ()


def entry_execution(order, bar, costs, *, max_gap, min_reward_risk):
    """Check reachability and price gates for an order active for one session."""
    opening = bar.open
    if order.kind == "limit":
        if opening <= order.stop:
            return None, "open_at_or_below_stop"
        if bar.low > order.reference:
            return None, "untouched"
        raw = min(opening, order.reference)
    elif order.kind == "stop":
        if bar.high < order.reference:
            return None, "untouched"
        raw = max(opening, order.reference)
    else:
        raw = opening
    if raw > order.reference * (1 + max_gap):
        return None, "gap_above_cap"
    limit = order.reference if order.kind == "limit" else None
    fill = costs.fill(raw, "buy", limit)
    # Same gate as v5.4.1, on the slipped economic price before explicit fees.
    economic_price = fill.price + fill.residual_slippage_per_unit
    if not order.stop < economic_price < order.target:
        return None, "inverted_bracket"
    if (order.target - economic_price) / (economic_price - order.stop) < min_reward_risk:
        return None, "reward_risk"
    return fill, "entry"


@dataclass(frozen=True)
class Exit:
    reason: str
    fill: Fill


def opening_exit(order, bar, costs, *, expired):
    """Handle resting positions at the open, preserving time-exit priority."""
    if expired:
        return Exit("time", costs.fill(bar.open, "sell"))
    if bar.open <= order.stop:
        return Exit("gap_stop", costs.fill(bar.open, "sell"))
    if bar.open >= order.target:
        return Exit("gap_target", costs.fill(bar.open, "sell", order.target))
    return None


def route_exit(order, bar, costs, assumption, *, new_position):
    path = bar.path(assumption)
    if new_position and order.kind != "market":
        path = first_touch(path, order.reference, upward=order.kind == "stop")
        if not path:
            raise ValueError("Entry accepted without a corresponding path touch")
    start = path[0]
    if start <= order.stop:
        return Exit("stop", costs.fill(start, "sell"))
    if start >= order.target:
        return Exit("target", costs.fill(start, "sell", order.target))
    for prior, current in zip(path, path[1:]):
        if current <= order.stop < prior:
            return Exit("stop", costs.fill(order.stop, "sell"))
        if prior < order.target <= current:
            return Exit("target", costs.fill(order.target, "sell", order.target))
    return None


def intraday_exit(order, bar, costs, assumption, *, new_position):
    if assumption != "conservative":
        return route_exit(order, bar, costs, assumption, new_position=new_position)
    high_first = route_exit(order, bar, costs, "HL", new_position=new_position)
    low_first = route_exit(order, bar, costs, "LH", new_position=new_position)
    priority = {"stop": 0, None: 1, "target": 2}
    return min((high_first, low_first), key=lambda result: priority[result.reason if result else None])
