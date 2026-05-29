from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from simulador.domain.entities import CapturedTrajectory


class CaptureRepository(ABC):
    @abstractmethod
    def save(self, trajectory: CapturedTrajectory) -> Path:
        raise NotImplementedError

    @abstractmethod
    def load(self, file_path: Path) -> CapturedTrajectory:
        raise NotImplementedError


class TrajectoryCalculationGateway(ABC):
    @abstractmethod
    def calculate(self, file_path: Path) -> dict[str, object]:
        raise NotImplementedError