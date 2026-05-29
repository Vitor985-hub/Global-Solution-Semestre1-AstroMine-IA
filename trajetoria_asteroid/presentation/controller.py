from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from trajetoria_asteroid.application.use_cases import OptimizeTrajectoryUseCase
from trajetoria_asteroid.domain.entities import OptimizationWeights, StateVector3D, TrajectoryWindow
from trajetoria_asteroid.infrastructure.qiskit_optimizer import QiskitTrajectoryOptimizer
from trajetoria_asteroid.infrastructure.trajectory_plotter import save_trajectory_animation, save_trajectory_plot


class TrajectoryController:
    def __init__(self) -> None:
        self.use_case = OptimizeTrajectoryUseCase(optimizer=QiskitTrajectoryOptimizer())
        self.default_plot_path = Path(__file__).resolve().parent.parent / "grafico_trajeto.png"
        self.default_animation_path = Path(__file__).resolve().parent.parent / "grafico_trajeto_animado.gif"

    def optimize_sample_trajectory(self) -> dict[str, object]:
        result = self.use_case.execute(sample_windows(), weights=OptimizationWeights())
        return self._serialize_result(result)

    def optimize_windows(
        self,
        windows: list[TrajectoryWindow],
        weights: OptimizationWeights | None = None,
    ) -> dict[str, object]:
        result = self.use_case.execute(windows, weights=weights or OptimizationWeights())
        return self._serialize_result(result)

    def plot_sample_trajectory(self, output_path: Path | None = None) -> Path:
        windows = sample_windows()
        result = self.use_case.execute(windows, weights=OptimizationWeights())
        return save_trajectory_plot(
            windows=windows,
            selected_window_name=result.selected_window.name,
            output_path=output_path or self.default_plot_path,
        )

    def plot_windows(
        self,
        windows: list[TrajectoryWindow],
        output_path: Path | None = None,
        weights: OptimizationWeights | None = None,
    ) -> Path:
        result = self.use_case.execute(windows, weights=weights or OptimizationWeights())
        return save_trajectory_plot(
            windows=windows,
            selected_window_name=result.selected_window.name,
            output_path=output_path or self.default_plot_path,
        )

    def animate_sample_trajectory(self, output_path: Path | None = None) -> Path:
        windows = sample_windows()
        result = self.use_case.execute(windows, weights=OptimizationWeights())
        return save_trajectory_animation(
            windows=windows,
            selected_window_name=result.selected_window.name,
            output_path=output_path or self.default_animation_path,
        )

    def animate_windows(
        self,
        windows: list[TrajectoryWindow],
        output_path: Path | None = None,
        weights: OptimizationWeights | None = None,
    ) -> Path:
        result = self.use_case.execute(windows, weights=weights or OptimizationWeights())
        return save_trajectory_animation(
            windows=windows,
            selected_window_name=result.selected_window.name,
            output_path=output_path or self.default_animation_path,
        )

    def _serialize_result(self, result) -> dict[str, object]:
        return {
            "selected_window": {
                "name": result.selected_window.name,
                "elapsed_days": result.selected_window.elapsed_days,
                "asteroid_position_km": asdict(result.selected_window.asteroid_position_km),
                "asteroid_velocity_km_s": asdict(result.selected_window.asteroid_velocity_km_s),
            },
            "metrics": {
                "offset": result.offset,
                "best_probability": result.best_probability,
                "window_cost": result.window_cost,
            },
        }


def sample_windows() -> list[TrajectoryWindow]:
    return [
        TrajectoryWindow(
            name="janela_7_dias",
            elapsed_days=7.0,
            asteroid_position_km=StateVector3D(148_900_000.0, 12_500_000.0, 4_000.0),
            asteroid_velocity_km_s=StateVector3D(-12.0, 19.0, 0.2),
        ),
        TrajectoryWindow(
            name="janela_21_dias",
            elapsed_days=21.0,
            asteroid_position_km=StateVector3D(151_300_000.0, 4_800_000.0, 2_500.0),
            asteroid_velocity_km_s=StateVector3D(-9.0, 17.0, -0.1),
        ),
        TrajectoryWindow(
            name="janela_45_dias",
            elapsed_days=45.0,
            asteroid_position_km=StateVector3D(154_100_000.0, -2_400_000.0, 1_500.0),
            asteroid_velocity_km_s=StateVector3D(-7.0, 15.0, 0.0),
        ),
    ]