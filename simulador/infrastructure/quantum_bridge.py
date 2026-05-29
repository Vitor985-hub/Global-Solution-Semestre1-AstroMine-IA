from __future__ import annotations

from pathlib import Path

import numpy as np

from simulador.infrastructure.json_capture_repository import JsonCaptureRepository
from trajetoria_asteroid.domain.entities import OptimizationWeights, StateVector3D, TrajectoryWindow
from trajetoria_asteroid.presentation.controller import TrajectoryController


PREDICTION_DAY_WINDOWS = [7.0, 14.0, 21.0, 28.0]


def _fit_quadratic_series(times: np.ndarray, values: np.ndarray) -> np.ndarray:
    degree = min(2, len(times) - 1)
    if degree <= 0:
        return np.array([0.0, 0.0, float(values[-1])], dtype=float)

    coefficients = np.polyfit(times, values, degree)
    if degree == 1:
        slope, intercept = coefficients
        return np.array([0.0, float(slope), float(intercept)], dtype=float)

    return coefficients.astype(float)


def _evaluate_quadratic(coefficients: np.ndarray, value: float) -> float:
    return float(np.polyval(coefficients, value))


def _quadratic_derivative(coefficients: np.ndarray, value: float) -> float:
    a_coeff, b_coeff, _ = coefficients
    return float((2.0 * a_coeff * value) + b_coeff)


def build_windows_from_capture_file(file_path: Path) -> list[TrajectoryWindow]:
    capture = JsonCaptureRepository(file_path).load(file_path)
    if len(capture.points) < 3:
        raise ValueError("Capture ao menos 3 pontos para enviar a trajetoria ao modulo quantico.")

    base_timestamp = capture.points[0].timestamp
    capture_times = np.array([point.timestamp - base_timestamp for point in capture.points], dtype=float)
    capture_x = np.array([point.x for point in capture.points], dtype=float)
    capture_y = np.array([point.y for point in capture.points], dtype=float)

    x_curve = _fit_quadratic_series(capture_times, capture_x)
    y_curve = _fit_quadratic_series(capture_times, capture_y)
    max_time = float(capture_times[-1]) if len(capture_times) else 0.0
    horizon_step = 0.5

    windows: list[TrajectoryWindow] = []
    for index, elapsed_days in enumerate(PREDICTION_DAY_WINDOWS, start=1):
        future_time = max_time + (index * horizon_step)
        predicted_x = _evaluate_quadratic(x_curve, future_time)
        predicted_y = _evaluate_quadratic(y_curve, future_time)
        velocity_x = _quadratic_derivative(x_curve, future_time)
        velocity_y = _quadratic_derivative(y_curve, future_time)
        position = StateVector3D(
            x=149_000_000.0 + predicted_x * 120.0,
            y=predicted_y * 120.0,
            z=capture.direction_degrees * 15.0 + (future_time * 25.0),
        )
        velocity = StateVector3D(
            x=max(abs(velocity_x) / 8.0, 0.1),
            y=velocity_y / 8.0,
            z=capture.total_distance_px / max(len(capture.points), 1_000.0),
        )
        windows.append(
            TrajectoryWindow(
                name=f"captura_nao_linear_{elapsed_days:.0f}_dias",
                elapsed_days=elapsed_days,
                asteroid_position_km=position,
                asteroid_velocity_km_s=velocity,
            )
        )

    return windows


def calculate_trajectory_from_capture(file_path: Path) -> dict[str, object]:
    windows = build_windows_from_capture_file(file_path)
    controller = TrajectoryController()
    return controller.optimize_windows(windows, weights=OptimizationWeights())