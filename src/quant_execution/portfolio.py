"""Apply corrected fills to the original long-only sizing and session order."""

from dataclasses import dataclass

from quant_execution.execution import Bar, Costs, Order, entry_execution, intraday_exit, opening_exit


@dataclass(frozen=True)
class Position:
    order: Order
    signal: object
    entered: object
    entry_index: int
    quantity: float
    entry: object


def simulate(label, dates, daybars, candidates, settings, assumption):
    hold_days = settings["hold_days_trend" if label == "돌파" else "hold_days_range"]
    costs = Costs(settings["fee_bps"], settings["slippage_bps"])
    cash = float(settings["initial_capital"])
    positions, marks = {}, {}
    entries, exits, equity = [], [], []
    pending = []

    def sell(symbol, date, result):
        nonlocal cash
        position = positions.pop(symbol)
        cash += position.quantity * result.fill.cash_per_unit
        exits.append((symbol, position.signal, position.entered, date,
                      result.fill.price, position.quantity, result.reason))

    for index, date in enumerate(dates):
        bars = {
            symbol: Bar(float(row.Open), float(row.High), float(row.Low), float(row.Close))
            for symbol, row in daybars[date].items()
        }
        for symbol, position in list(positions.items()):
            if symbol in bars:
                result = opening_exit(position.order, bars[symbol], costs,
                                      expired=index - position.entry_index >= hold_days)
                if result:
                    sell(symbol, date, result)

        for candidate in pending:
            symbol = candidate["종목"]
            if (candidate["전략"] != label or symbol not in bars or symbol in positions
                    or len(positions) >= settings["max_positions"]):
                continue
            kind = {"limit_entry": "limit", "stop_entry": "stop", "next_open": "market"}
            order = Order(kind[candidate["진입방식"]], candidate["참고진입가"],
                          candidate["손절"], candidate["목표"])
            fill, _ = entry_execution(order, bars[symbol], costs,
                                      max_gap=settings["max_gap_pct"],
                                      min_reward_risk=settings["min_executable_rr"])
            if fill is None:
                continue
            opening_nav = cash + sum(
                position.quantity * (bars[ticker].open if ticker in bars
                                     else marks.get(ticker, position.entry.price))
                for ticker, position in positions.items()
            )
            budget = min(settings["allocation_per_position"] * opening_nav, cash)
            if budget < 25:
                continue
            quantity = budget / fill.cash_per_unit
            cash -= quantity * fill.cash_per_unit
            signal = candidate["신호일"]
            positions[symbol] = Position(order, signal, date, index, quantity, fill)
            entries.append((symbol, signal, date, fill.price, quantity))

        # Funds from intraday exits do not finance orders examined that session.
        for symbol, position in list(positions.items()):
            if symbol in bars:
                result = intraday_exit(position.order, bars[symbol], costs, assumption,
                                       new_position=position.entry_index == index)
                if result:
                    sell(symbol, date, result)
        marks.update({symbol: bar.close for symbol, bar in bars.items()})
        nav = cash + sum(position.quantity * marks[symbol] for symbol, position in positions.items())
        if cash < -1e-6 or nav <= 0:
            raise ValueError("Invalid account balance")
        equity.append(nav)
        pending = candidates.get(date, [])
    return equity, entries, exits
