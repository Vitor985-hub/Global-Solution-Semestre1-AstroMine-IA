from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class StateVector3D:
    x: float
    y: float
    z: float

    def distance_to(self, other: "StateVector3D") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return sqrt(dx * dx + dy * dy + dz * dz)


@dataclass(frozen=True)
class TrajectoryWindow:
    name: str
    elapsed_days: float
    asteroid_position_km: StateVector3D
    asteroid_velocity_km_s: StateVector3D


@dataclass(frozen=True)
class OptimizationWeights:
    distance: float = 1.0
    speed: float = 0.4
    earth_rotation: float = 0.2
    earth_translation: float = 0.8
    single_choice_penalty: float = 35.0


@dataclass(frozen=True)
class OptimizationResult:
    selected_window: TrajectoryWindow
    offset: float
    best_probability: float
    window_cost: float