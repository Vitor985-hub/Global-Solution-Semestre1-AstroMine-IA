from __future__ import annotations

from pathlib import Path

from simulador.application.ports import TrajectoryCalculationGateway
from simulador.infrastructure.quantum_bridge import calculate_trajectory_from_capture


class QuantumTrajectoryGateway(TrajectoryCalculationGateway):
    def calculate(self, file_path: Path) -> dict[str, object]:
        return calculate_trajectory_from_capture(file_path)