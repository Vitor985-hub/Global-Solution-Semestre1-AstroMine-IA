from __future__ import annotations

from math import cos, pi, sin, sqrt
from typing import Sequence

from trajetoria_asteroid.domain.entities import OptimizationWeights, StateVector3D, TrajectoryWindow


EARTH_ROTATION_PERIOD_SECONDS = 86_164.0
EARTH_TRANSLATION_PERIOD_DAYS = 365.25
EARTH_ORBIT_RADIUS_KM = 149_597_870.7


def earth_translation_position(elapsed_days: float) -> StateVector3D:
    angle = 2.0 * pi * (elapsed_days / EARTH_TRANSLATION_PERIOD_DAYS)
    return StateVector3D(
        x=EARTH_ORBIT_RADIUS_KM * cos(angle),
        y=EARTH_ORBIT_RADIUS_KM * sin(angle),
        z=0.0,
    )


def earth_rotation_angle(elapsed_days: float) -> float:
    elapsed_seconds = elapsed_days * 24.0 * 60.0 * 60.0
    return (2.0 * pi * elapsed_seconds / EARTH_ROTATION_PERIOD_SECONDS) % (2.0 * pi)


def build_window_cost(window: TrajectoryWindow, weights: OptimizationWeights) -> float:
    earth_position = earth_translation_position(window.elapsed_days)
    earth_rotation = earth_rotation_angle(window.elapsed_days)
    distance_cost = earth_position.distance_to(window.asteroid_position_km) / 1_000_000.0
    speed_cost = sqrt(
        window.asteroid_velocity_km_s.x ** 2
        + window.asteroid_velocity_km_s.y ** 2
        + window.asteroid_velocity_km_s.z ** 2
    )
    translation_alignment = abs(window.asteroid_position_km.z) / 1_000_000.0
    rotation_alignment = 1.0 - cos(earth_rotation)
    return (
        weights.distance * distance_cost
        + weights.speed * speed_cost
        + weights.earth_translation * translation_alignment
        + weights.earth_rotation * rotation_alignment
    )


def build_qubo_coefficients(
    windows: Sequence[TrajectoryWindow],
    weights: OptimizationWeights,
) -> tuple[list[float], dict[tuple[int, int], float]]:
    linear = [build_window_cost(window, weights) - weights.single_choice_penalty for window in windows]
    quadratic: dict[tuple[int, int], float] = {}

    for left in range(len(windows)):
        for right in range(left + 1, len(windows)):
            quadratic[(left, right)] = 2.0 * weights.single_choice_penalty

    return linear, quadratic