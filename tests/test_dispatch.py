import unittest
from dispatch import distance, generate, simulate, summary


class DispatchTests(unittest.TestCase):
    def test_seeded_comparison(self):
        orders = generate(40, 30, seed=3)
        near = simulate(orders, 5, "nearest", seed=3)
        first = simulate(orders, 5, "first", seed=3)
        self.assertEqual({r["order_id"] for r in near}, set(range(40)))
        self.assertLessEqual(summary(near)["average_pickup_distance"], summary(first)["average_pickup_distance"])

    def test_distance_and_empty(self):
        self.assertEqual(distance((1, 2), (4, 5)), 6)
        self.assertEqual(summary(simulate([], 1))["orders"], 0)

