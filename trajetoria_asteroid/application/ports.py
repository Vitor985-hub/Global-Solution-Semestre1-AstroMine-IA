from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from trajetoria_asteroid.domain.entities import OptimizationResult, OptimizationWeights, TrajectoryWindow


class TrajectoryOptimizer(ABC):
    @abstractmethod
    def optimize(
        self,
        windows: Sequence[TrajectoryWindow],
        weights: OptimizationWeights,
        reps: int = 2,
    ) -> OptimizationResult:
        raise NotImplementedError