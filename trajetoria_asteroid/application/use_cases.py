from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from trajetoria_asteroid.application.ports import TrajectoryOptimizer
from trajetoria_asteroid.domain.entities import OptimizationResult, OptimizationWeights, TrajectoryWindow


@dataclass
class OptimizeTrajectoryUseCase:
    optimizer: TrajectoryOptimizer

    def execute(
        self,
        windows: Sequence[TrajectoryWindow],
        weights: OptimizationWeights | None = None,
        reps: int = 2,
    ) -> OptimizationResult:
        if not windows:
            raise ValueError("Forneca ao menos uma janela de trajetoria.")

        current_weights = weights or OptimizationWeights()
        return self.optimizer.optimize(windows, current_weights, reps=reps)