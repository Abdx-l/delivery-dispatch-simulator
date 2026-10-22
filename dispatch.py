"""Compare distance-aware and first-available courier dispatch."""
import argparse
import csv
import heapq
import json
import random
from dataclasses import dataclass


@dataclass
class Courier:
    id: int
    x: int
    y: int
    busy_until: int = 0


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def generate(order_count, ticks, seed=7, grid=30):
    rng = random.Random(seed)
    return sorted([(rng.randrange(ticks), i, (rng.randrange(grid), rng.randrange(grid)),
                    (rng.randrange(grid), rng.randrange(grid))) for i in range(order_count)])


def simulate(orders, courier_count=50, policy="nearest", grid=30, seed=7):
    if courier_count < 1 or policy not in ("nearest", "first"):
        raise ValueError("invalid couriers or policy")
    rng = random.Random(seed)
    couriers = [Courier(i, rng.randrange(grid), rng.randrange(grid)) for i in range(courier_count)]
    pending = []
    assignments = []
    tick = 0
    remaining = iter(orders)
    upcoming = next(remaining, None)
    while upcoming is not None or pending:
        while upcoming is not None and upcoming[0] <= tick:
            pending.append(upcoming)
            upcoming = next(remaining, None)
        for courier in couriers:
            if courier.busy_until == tick and hasattr(courier, "destination"):
                courier.x, courier.y = courier.destination
                del courier.destination
        for order in pending[:]:
            available = [c for c in couriers if c.busy_until <= tick]
            if not available:
                break
            pickup = order[2]
            if policy == "nearest":
                heap = [(distance((c.x, c.y), pickup), c.id, c) for c in available]
                heapq.heapify(heap)
                pickup_distance, _, courier = heapq.heappop(heap)
            else:
                courier = min(available, key=lambda c: c.id)
                pickup_distance = distance((courier.x, courier.y), pickup)
            travel = pickup_distance + distance(pickup, order[3])
            courier.busy_until = tick + max(1, travel)
            courier.destination = order[3]
            assignments.append({"order_id": order[1], "created_tick": order[0], "assigned_tick": tick,
                                "courier_id": courier.id, "pickup_distance": pickup_distance,
                                "complete_tick": courier.busy_until})
            pending.remove(order)
        tick += 1
    return assignments


def summary(assignments):
    count = len(assignments)
    return {"orders": count, "average_pickup_distance": round(sum(a["pickup_distance"] for a in assignments) / count, 2) if count else 0,
            "average_wait_ticks": round(sum(a["assigned_tick"] - a["created_tick"] for a in assignments) / count, 2) if count else 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--orders", type=int, default=1000)
    p.add_argument("--couriers", type=int, default=50)
    p.add_argument("--ticks", type=int, default=600)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--csv")
    a = p.parse_args()
    if a.orders < 0 or a.ticks < 1:
        p.error("orders must be nonnegative and ticks positive")
    orders = generate(a.orders, a.ticks, a.seed)
    results = {policy: simulate(orders, a.couriers, policy, seed=a.seed) for policy in ("nearest", "first")}
    print(json.dumps({policy: summary(rows) for policy, rows in results.items()}, indent=2))
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["policy", "order_id", "created_tick", "assigned_tick", "courier_id", "pickup_distance", "complete_tick"])
            writer.writeheader()
            for policy, rows in results.items():
                writer.writerows({"policy": policy, **row} for row in rows)


if __name__ == "__main__":
    main()

