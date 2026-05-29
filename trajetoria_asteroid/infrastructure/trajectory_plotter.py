from __future__ import annotations

from datetime import datetime, timedelta
from math import cos, pi, sin
from pathlib import Path
from typing import Sequence

import matplotlib
import numpy as np

matplotlib.use("Agg")

from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.pyplot as plt

from trajetoria_asteroid.domain.entities import TrajectoryWindow
from trajetoria_asteroid.domain.services import earth_translation_position


def _configure_axis(axis, reference_datetime: datetime) -> None:
    axis.set_title(f"Trajetoria estimada do asteroide\nReferencia: {reference_datetime.strftime('%d/%m/%Y %H:%M')}")
    axis.set_xlabel("X (km)")
    axis.set_ylabel("Y (km)")
    axis.set_zlabel("Z (km)")
    axis.view_init(elev=24, azim=48)


def _orbit_points(steps: int = 180) -> tuple[list[float], list[float], list[float]]:
    orbit_radius_km = earth_translation_position(0.0).x
    orbit_angles = [2.0 * pi * step / float(steps) for step in range(steps + 1)]
    orbit_x = [orbit_radius_km * cos(angle) for angle in orbit_angles]
    orbit_y = [orbit_radius_km * sin(angle) for angle in orbit_angles]
    orbit_z = [0.0 for _ in orbit_angles]
    return orbit_x, orbit_y, orbit_z


def _fit_axis_curve(times: np.ndarray, values: np.ndarray) -> np.ndarray:
    degree = min(2, len(times) - 1)
    if degree <= 0:
        return np.array([0.0, 0.0, float(values[-1])], dtype=float)

    coefficients = np.polyfit(times, values, degree)
    if degree == 1:
        slope, intercept = coefficients
        return np.array([0.0, float(slope), float(intercept)], dtype=float)

    return coefficients.astype(float)


def _nonlinear_curve_points(
    windows: Sequence[TrajectoryWindow],
    samples: int = 120,
) -> tuple[list[float], list[float], list[float], list[float], np.ndarray, np.ndarray, np.ndarray]:
    elapsed_days = np.array([window.elapsed_days for window in windows], dtype=float)
    x_values = np.array([window.asteroid_position_km.x for window in windows], dtype=float)
    y_values = np.array([window.asteroid_position_km.y for window in windows], dtype=float)
    z_values = np.array([window.asteroid_position_km.z for window in windows], dtype=float)

    x_curve = _fit_axis_curve(elapsed_days, x_values)
    y_curve = _fit_axis_curve(elapsed_days, y_values)
    z_curve = _fit_axis_curve(elapsed_days, z_values)

    dense_days = np.linspace(float(elapsed_days[0]), float(elapsed_days[-1]), samples)
    dense_x = np.polyval(x_curve, dense_days)
    dense_y = np.polyval(y_curve, dense_days)
    dense_z = np.polyval(z_curve, dense_days)
    return (
        dense_days.tolist(),
        dense_x.tolist(),
        dense_y.tolist(),
        dense_z.tolist(),
        x_curve,
        y_curve,
        z_curve,
    )


def save_trajectory_plot(
    windows: Sequence[TrajectoryWindow],
    selected_window_name: str,
    output_path: Path,
) -> Path:
    reference_datetime = datetime.now().astimezone()
    figure = plt.figure(figsize=(12, 7))
    axis = figure.add_subplot(111, projection="3d")

    orbit_x, orbit_y, orbit_z = _orbit_points()

    x_values = [window.asteroid_position_km.x for window in windows]
    y_values = [window.asteroid_position_km.y for window in windows]
    z_values = [window.asteroid_position_km.z for window in windows]
    _, smooth_x, smooth_y, smooth_z, _, _, _ = _nonlinear_curve_points(windows)

    selected_window = next(window for window in windows if window.name == selected_window_name)
    current_earth_position = earth_translation_position(0.0)
    selected_earth_position = earth_translation_position(selected_window.elapsed_days)
    selected_arrival_time = reference_datetime + timedelta(days=selected_window.elapsed_days)

    axis.plot(
        orbit_x,
        orbit_y,
        orbit_z,
        color="#adb5bd",
        linewidth=1.2,
        linestyle="--",
        alpha=0.9,
        label="orbita da Terra",
    )

    axis.scatter(0.0, 0.0, 0.0, color="#ffb703", s=220, marker="*", label="Sol")
    axis.text(0.0, 0.0, 0.0, " Sol", fontsize=10)

    axis.scatter(
        current_earth_position.x,
        current_earth_position.y,
        current_earth_position.z,
        color="#3a86ff",
        s=75,
        marker="o",
        label="Terra agora",
    )
    axis.text(
        current_earth_position.x,
        current_earth_position.y,
        current_earth_position.z,
        f" Terra agora {reference_datetime.strftime('%d/%m %H:%M')}",
        fontsize=8,
    )

    axis.plot(smooth_x, smooth_y, smooth_z, color="#2a9d8f", linewidth=2.5, label="trajeto nao linear do asteroide")

    for window in windows:
        earth_position = earth_translation_position(window.elapsed_days)
        timestamp = reference_datetime + timedelta(days=window.elapsed_days)
        is_selected = window.name == selected_window_name
        asteroid_color = "#e63946" if is_selected else "#264653"
        earth_color = "#8338ec" if is_selected else "#8ecae6"
        size = 110 if is_selected else 42
        axis.scatter(
            window.asteroid_position_km.x,
            window.asteroid_position_km.y,
            window.asteroid_position_km.z,
            color=asteroid_color,
            s=size,
            label="janela otima" if is_selected else None,
        )
        axis.text(
            window.asteroid_position_km.x,
            window.asteroid_position_km.y,
            window.asteroid_position_km.z,
            f" {window.name}{' (otima)' if is_selected else ''}",
            fontsize=8,
        )
        axis.scatter(
            earth_position.x,
            earth_position.y,
            earth_position.z,
            color=earth_color,
            s=85 if is_selected else 55,
            marker="o",
            label="Terra na chegada" if is_selected else None,
        )
        axis.plot(
            [0.0, earth_position.x],
            [0.0, earth_position.y],
            [0.0, earth_position.z],
            color=earth_color,
            linewidth=1.4 if is_selected else 1.0,
            alpha=0.8 if is_selected else 0.35,
        )
        axis.text(
            earth_position.x,
            earth_position.y,
            earth_position.z,
            f" Terra {timestamp.strftime('%d/%m %H:%M')}",
            fontsize=8,
        )

    axis.plot(
        [selected_earth_position.x, selected_window.asteroid_position_km.x],
        [selected_earth_position.y, selected_window.asteroid_position_km.y],
        [selected_earth_position.z, selected_window.asteroid_position_km.z],
        color="#fb5607",
        linewidth=1.8,
        linestyle=":",
        label="transferencia escolhida",
    )
    axis.text(
        selected_window.asteroid_position_km.x,
        selected_window.asteroid_position_km.y,
        selected_window.asteroid_position_km.z,
        f" chegada {selected_arrival_time.strftime('%d/%m %H:%M')}",
        fontsize=8,
    )

    _configure_axis(axis, reference_datetime)
    axis.legend(loc="upper left")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)
    return output_path


def save_trajectory_animation(
    windows: Sequence[TrajectoryWindow],
    selected_window_name: str,
    output_path: Path,
) -> Path:
    reference_datetime = datetime.now().astimezone()
    figure = plt.figure(figsize=(12, 7))
    axis = figure.add_subplot(111, projection="3d")

    orbit_x, orbit_y, orbit_z = _orbit_points()
    x_values = [window.asteroid_position_km.x for window in windows]
    y_values = [window.asteroid_position_km.y for window in windows]
    z_values = [window.asteroid_position_km.z for window in windows]
    selected_window = next(window for window in windows if window.name == selected_window_name)
    smooth_days, smooth_x, smooth_y, smooth_z, x_curve, y_curve, z_curve = _nonlinear_curve_points(windows)
    total_frames = 36

    min_x = min([0.0, *orbit_x, *x_values, *smooth_x])
    max_x = max([0.0, *orbit_x, *x_values, *smooth_x])
    min_y = min([0.0, *orbit_y, *y_values, *smooth_y])
    max_y = max([0.0, *orbit_y, *y_values, *smooth_y])
    min_z = min([0.0, *z_values, *smooth_z])
    max_z = max([0.0, *z_values, *smooth_z])
    padding_xy = 10_000_000.0
    padding_z = 5_000.0

    def update(frame_index: int) -> None:
        axis.cla()
        progress = frame_index / max(total_frames - 1, 1)
        elapsed_days = selected_window.elapsed_days * progress
        earth_position = earth_translation_position(elapsed_days)
        current_time = reference_datetime + timedelta(days=elapsed_days)
        asteroid_x = float(np.polyval(x_curve, elapsed_days))
        asteroid_y = float(np.polyval(y_curve, elapsed_days))
        asteroid_z = float(np.polyval(z_curve, elapsed_days))

        axis.plot(orbit_x, orbit_y, orbit_z, color="#adb5bd", linewidth=1.2, linestyle="--", alpha=0.9)
        axis.scatter(0.0, 0.0, 0.0, color="#ffb703", s=220, marker="*")
        axis.text(0.0, 0.0, 0.0, " Sol", fontsize=10)

        axis.plot(smooth_x, smooth_y, smooth_z, color="#94d2bd", linewidth=1.8, alpha=0.65)
        visible_samples = max(2, int(progress * len(smooth_days)))
        axis.plot(smooth_x[:visible_samples], smooth_y[:visible_samples], smooth_z[:visible_samples], color="#2a9d8f", linewidth=2.2)
        axis.plot(
            [0.0, earth_position.x],
            [0.0, earth_position.y],
            [0.0, earth_position.z],
            color="#3a86ff",
            linewidth=1.2,
            alpha=0.7,
        )
        axis.plot(
            [earth_position.x, asteroid_x],
            [earth_position.y, asteroid_y],
            [earth_position.z, asteroid_z],
            color="#fb5607",
            linewidth=1.8,
            linestyle=":",
            alpha=0.85,
        )

        axis.scatter(earth_position.x, earth_position.y, earth_position.z, color="#3a86ff", s=85, marker="o")
        axis.text(
            earth_position.x,
            earth_position.y,
            earth_position.z,
            f" Terra {current_time.strftime('%d/%m %H:%M')}",
            fontsize=8,
        )

        axis.scatter(asteroid_x, asteroid_y, asteroid_z, color="#e63946", s=110)
        axis.text(asteroid_x, asteroid_y, asteroid_z, f" asteroide t+{elapsed_days:.1f}d", fontsize=8)

        axis.scatter(
            selected_window.asteroid_position_km.x,
            selected_window.asteroid_position_km.y,
            selected_window.asteroid_position_km.z,
            color="#264653",
            s=45,
            alpha=0.35,
        )
        axis.text(
            selected_window.asteroid_position_km.x,
            selected_window.asteroid_position_km.y,
            selected_window.asteroid_position_km.z,
            f" chegada {selected_window.elapsed_days:.0f}d",
            fontsize=8,
        )

        axis.set_xlim(min_x - padding_xy, max_x + padding_xy)
        axis.set_ylim(min_y - padding_xy, max_y + padding_xy)
        axis.set_zlim(min_z - padding_z, max_z + padding_z)
        _configure_axis(axis, reference_datetime)
        axis.set_title(
            "Animacao da trajetoria do asteroide\n"
            f"Referencia: {reference_datetime.strftime('%d/%m/%Y %H:%M')} | Tempo simulado: {current_time.strftime('%d/%m %H:%M')}"
        )

    animation = FuncAnimation(figure, update, frames=total_frames, interval=140, repeat=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(output_path, writer=PillowWriter(fps=8))
    plt.close(figure)
    return output_path