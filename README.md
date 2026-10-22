# Delivery Dispatch Simulator

Simulate couriers on a city grid and compare nearest-available matching with a first-available baseline. Both policies see the same seeded order stream. Orders are assigned to idle couriers; moving couriers advance one grid step per tick and become available at drop-off.

```sh
python dispatch.py --orders 1000 --couriers 50 --ticks 600 --seed 7 --csv assignments.csv
python -m unittest discover -s tests -v
```

The CSV records assignment tick, courier, pickup distance, and completion tick. This standalone simulator uses in-memory positions and a heap for nearest-courier selection. It reports average pickup distance and wait ticks for each policy.

