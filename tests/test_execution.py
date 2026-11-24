import unittest
from types import SimpleNamespace

from quant_execution.execution import Bar, Costs, Order, entry_execution, intraday_exit, opening_exit
from quant_execution.portfolio import simulate


class ExecutionTests(unittest.TestCase):
    costs = Costs(5, 5)
    stop_buy = Order("stop", 105, 100, 115)
    limit_buy = Order("limit", 100, 95, 109)

    def entry(self, order, bar):
        return entry_execution(order, bar, self.costs, max_gap=.08, min_reward_risk=1.2)

    def test_post_entry_stop_counts(self):
        result = intraday_exit(self.stop_buy, Bar(103, 111, 97, 105), self.costs, "HL", new_position=True)
        self.assertEqual(result.reason, "stop")
        self.assertAlmostEqual(result.fill.price, 99.95)

    def test_both_exit_levels_after_open_entry(self):
        order = Order("market", 105, 100, 115)
        bar = Bar(105, 116, 99, 105)
        for path, reason in (("HL", "target"), ("LH", "stop"), ("conservative", "stop")):
            with self.subTest(path=path):
                self.assertEqual(intraday_exit(order, bar, self.costs, path, new_position=True).reason, reason)

    def test_ambiguous_target_vs_holding(self):
        bar = Bar(103, 111, 98, 100)
        self.assertIsNone(intraday_exit(self.limit_buy, bar, self.costs, "conservative", new_position=True))
        self.assertEqual(intraday_exit(self.limit_buy, bar, self.costs, "LH", new_position=True).reason, "target")

    def test_stop_entry_gap_fills_at_open_plus_slippage(self):
        fill, _ = self.entry(self.stop_buy, Bar(106, 110, 101, 107))
        self.assertAlmostEqual(fill.price, 106 * 1.0005)
        self.assertEqual(fill.residual_slippage_per_unit, 0)

    def test_excessive_gap_rejects_stop_entry(self):
        self.assertEqual(self.entry(self.stop_buy, Bar(114, 117, 110, 114)), (None, "gap_above_cap"))

    def test_market_entry_prices_at_open_and_has_no_limit(self):
        market = Order("market", 100, 95, 109)
        fill, _ = self.entry(market, Bar(101, 105, 98, 102))
        self.assertAlmostEqual(fill.price, 101 * 1.0005)
        self.assertGreater(fill.price, market.reference)

    def test_limit_price_improvement_on_open(self):
        fill, _ = self.entry(self.limit_buy, Bar(99, 101, 97, 100))
        self.assertAlmostEqual(fill.price, 99 * 1.0005)
        self.assertEqual(fill.residual_slippage_per_unit, 0)

    def test_limit_gap_beyond_stop_cancels(self):
        self.assertEqual(self.entry(self.limit_buy, Bar(94, 101, 92, 99)), (None, "open_at_or_below_stop"))

    def test_untouched_orders_do_not_fill(self):
        self.assertEqual(self.entry(self.limit_buy, Bar(101, 106, 101, 102)), (None, "untouched"))
        self.assertEqual(self.entry(self.stop_buy, Bar(103, 104, 97, 100)), (None, "untouched"))

    def test_open_gap_below_stop_exits_at_open(self):
        result = opening_exit(self.limit_buy, Bar(93, 96, 91, 94), self.costs, expired=False)
        self.assertEqual(result.reason, "gap_stop")
        self.assertAlmostEqual(result.fill.price, 93 * .9995)

    def test_open_gap_above_target_allows_improvement(self):
        result = opening_exit(self.limit_buy, Bar(110, 111, 107, 108), self.costs, expired=False)
        self.assertEqual(result.reason, "gap_target")
        self.assertAlmostEqual(result.fill.price, 110 * .9995)

    def test_fee_and_unapplied_slippage_booked_separately(self):
        buy = self.costs.fill(100, "buy", 100)
        sell = self.costs.fill(100, "sell", 100)
        self.assertAlmostEqual(buy.fee_per_unit, .05)
        self.assertAlmostEqual(buy.residual_slippage_per_unit, .05)
        self.assertAlmostEqual(buy.cash_per_unit, 100.1)
        self.assertAlmostEqual(sell.cash_per_unit, 99.9)

    def test_invalid_order_and_inconsistent_bar_fail(self):
        with self.assertRaises(ValueError):
            Order("limit", 100, 100, 110)
        with self.assertRaises(ValueError):
            Bar(100, 101, 102, 100)

    def test_ohlc_rounding_at_the_boundary(self):
        from math import nextafter

        bar = Bar(100, nextafter(100, 0), 98, 99)
        self.assertEqual(bar.path("HL"), (100, 100, 98, 99))

    def test_zero_range_bar_at_limit_keeps_position(self):
        bar = Bar(100, 100, 100, 100)
        fill, _ = self.entry(self.limit_buy, bar)
        self.assertEqual(fill.price, 100)
        self.assertIsNone(intraday_exit(self.limit_buy, bar, self.costs, "HL", new_position=True))


class PortfolioTests(unittest.TestCase):
    settings = {"hold_days_range": 5, "hold_days_trend": 20, "fee_bps": 5, "slippage_bps": 5,
                "initial_capital": 10_000, "max_positions": 1, "max_gap_pct": .08,
                "min_executable_rr": 1.2, "allocation_per_position": 1}

    def candidate(self, symbol):
        return {"종목": symbol, "전략": "횡보", "진입방식": "limit_entry", "참고진입가": 100,
                "손절": 95, "목표": 109, "신호일": 1}

    def bar(self, opening, high, low, close):
        return SimpleNamespace(Open=opening, High=high, Low=low, Close=close)

    def test_signal_next_session_sizing_and_no_intraday_fund_reuse(self):
        day = {"A": self.bar(103, 111, 98, 101), "B": self.bar(103, 111, 98, 101)}
        nav, entries, exits = simulate("횡보", (1, 2), {1: day, 2: day},
                                       {1: [self.candidate("A"), self.candidate("B")]}, self.settings, "LH")
        self.assertEqual(nav[0], 10_000)
        self.assertEqual([(x[0], x[2], x[3]) for x in entries], [("A", 2, 100)])
        self.assertEqual([(x[0], x[3], x[4]) for x in exits], [("A", 2, 109)])
        self.assertAlmostEqual(nav[1], 10_000 / 100.1 * (109 - .0545 - .0545))

    def test_untouched_pending_order_expires_that_session(self):
        day = {"A": self.bar(103, 111, 98, 101)}
        untouched = {"A": self.bar(103, 111, 101, 102)}
        nav, entries, exits = simulate("횡보", (1, 2, 3), {1: day, 2: untouched, 3: day},
                                       {1: [self.candidate("A")]}, self.settings, "LH")
        self.assertEqual((nav, entries, exits), ([10_000] * 3, [], []))
