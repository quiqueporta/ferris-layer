from typing import NamedTuple


class SweepKey(NamedTuple):
    position: tuple
    x: float
    y: float
    rotation: int = 0


SWEEP_KEYS = (
    SweepKey((0, 0), 0, 0.93),
    SweepKey((0, 1), 1, 0.31),
    SweepKey((0, 2), 2, 0),
    SweepKey((0, 3), 3, 0.28),
    SweepKey((0, 4), 4, 0.42),

    SweepKey((4, 0), 7, 0.42),
    SweepKey((4, 1), 8, 0.28),
    SweepKey((4, 2), 9, 0),
    SweepKey((4, 3), 10, 0.31),
    SweepKey((4, 4), 11, 0.93),

    SweepKey((1, 0), 0, 1.93),
    SweepKey((1, 1), 1, 1.31),
    SweepKey((1, 2), 2, 1),
    SweepKey((1, 3), 3, 1.28),
    SweepKey((1, 4), 4, 1.42),

    SweepKey((5, 0), 7, 1.42),
    SweepKey((5, 1), 8, 1.28),
    SweepKey((5, 2), 9, 1),
    SweepKey((5, 3), 10, 1.31),
    SweepKey((5, 4), 11, 1.93),

    SweepKey((2, 0), 0, 2.93),
    SweepKey((2, 1), 1, 2.31),
    SweepKey((2, 2), 2, 2),
    SweepKey((2, 3), 3, 2.28),
    SweepKey((2, 4), 4, 2.42),

    SweepKey((6, 0), 7, 2.42),
    SweepKey((6, 1), 8, 2.28),
    SweepKey((6, 2), 9, 2),
    SweepKey((6, 3), 10, 2.31),
    SweepKey((6, 4), 11, 2.93),

    SweepKey((3, 0), 3.5, 3.75, 15),
    SweepKey((3, 1), 4.5, 4, 30),

    SweepKey((7, 0), 6.5, 4, -30),
    SweepKey((7, 1), 7.5, 3.75, -15),
)
