from dataclasses import dataclass


@dataclass(frozen=True)
class Layer:
    number: int
    name: str

    def description(self):
        return f"Layer {self.number} · {self.name}"
