"""Synthetic counterparts of the four original-failure assertions."""

import unittest

from quant_execution.execution import Bar, Costs, Order, entry_execution, intraday_exit


class ExecutionRegressions(unittest.TestCase):
    costs = Costs(5, 5)

    def test_low_before_stop_entry_cannot_close_position(self):
        order = Order("stop", 105, 100, 115)
        bar = Bar(103, 111, 97, 105)
        self.assertIsNone(intraday_exit(order, bar, self.costs, "LH", new_position=True))

    def test_high_before_limit_entry_cannot_close_position(self):
        order = Order("limit", 100, 95, 109)
        bar = Bar(103, 111, 98, 100)
        self.assertIsNone(intraday_exit(order, bar, self.costs, "HL", new_position=True))

    def test_buy_limit_is_never_exceeded(self):
        fill, _ = entry_execution(Order("limit", 100, 95, 110), Bar(101, 102, 99, 100), self.costs,
                                  max_gap=.08, min_reward_risk=1.2)
        self.assertLessEqual(fill.price, 100)

    def test_sell_limit_is_never_undercut(self):
        result = intraday_exit(Order("limit", 100, 95, 109), Bar(103, 111, 98, 100), self.costs,
                               "LH", new_position=True)
        self.assertEqual(result.reason, "target")
        self.assertGreaterEqual(result.fill.price, 109)
