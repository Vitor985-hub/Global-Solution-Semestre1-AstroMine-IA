from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from simulador.application.ports import CaptureRepository, TrajectoryCalculationGateway
from simulador.domain.entities import CapturedTrajectory


@dataclass
class SaveCapturedTrajectoryUseCase:
    repository: CaptureRepository

    def execute(self, trajectory: CapturedTrajectory) -> Path:
        return self.repository.save(trajectory)


@dataclass
class CalculateTrajectoryFromCaptureUseCase:
    repository: CaptureRepository
    calculator: TrajectoryCalculationGateway

    def execute(self, file_path: Path) -> dict[str, object]:
        self.repository.load(file_path)
        return self.calculator.calculate(file_path)