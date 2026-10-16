from dataclasses import dataclass


@dataclass(frozen=True)
class Layer:
    number: int
    name: str
