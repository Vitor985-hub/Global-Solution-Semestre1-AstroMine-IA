from __future__ import annotations

from datetime import UTC, datetime
from math import atan2, degrees, hypot

from simulador.domain.entities import CapturedTrajectory, CaptureMetrics, MotionSnapshot, SimulationConfig, TrajectoryPoint


def build_motion_snapshot(current: TrajectoryPoint, previous: TrajectoryPoint | None) -> MotionSnapshot:
    if previous is None:
        return MotionSnapshot(speed_px_s=0.0, direction_degrees=0.0)

    delta_time = max(current.timestamp - previous.timestamp, 1e-6)
    delta_x = current.x - previous.x
    delta_y = current.y - previous.y
    return MotionSnapshot(
        speed_px_s=hypot(delta_x, delta_y) / delta_time,
        direction_degrees=degrees(atan2(delta_y, delta_x)),
    )


def calculate_total_distance(points: list[TrajectoryPoint]) -> float:
    total = 0.0
    for index in range(len(points) - 1):
        current = points[index]
        next_point = points[index + 1]
        total += hypot(current.x - next_point.x, current.y - next_point.y)
    return total


def should_stop_capture(
    started_at: float,
    last_motion_at: float | None,
    now: float,
    config: SimulationConfig,
) -> bool:
    if config.stop_on_idle and last_motion_at is not None and (now - last_motion_at) >= config.max_idle_seconds:
        return True
    return (now - started_at) >= config.max_capture_seconds


def describe_stop_reason(
    started_at: float,
    last_motion_at: float | None,
    now: float,
    config: SimulationConfig,
) -> str:
    if config.stop_on_idle and last_motion_at is not None:
        idle_for = now - last_motion_at
        if idle_for >= config.max_idle_seconds:
            return f"sem movimento por {idle_for:.1f}s"

    elapsed = now - started_at
    remaining = max(config.max_capture_seconds - elapsed, 0.0)
    return f"capturando por mais {remaining:.1f}s em passos de {config.frame_sampling_interval_seconds:.1f}s"


def build_capture_metrics(
    points: list[TrajectoryPoint],
    snapshot: MotionSnapshot,
    stop_reason: str,
) -> CaptureMetrics:
    return CaptureMetrics(
        total_distance_px=calculate_total_distance(points),
        tracked_points=len(points),
        speed_px_s=snapshot.speed_px_s,
        direction_degrees=snapshot.direction_degrees,
        stop_reason=stop_reason,
    )


def build_captured_trajectory(points: list[TrajectoryPoint], snapshot: MotionSnapshot) -> CapturedTrajectory:
    return CapturedTrajectory(
        captured_at=datetime.now(UTC),
        total_distance_px=calculate_total_distance(points),
        speed_px_s=snapshot.speed_px_s,
        direction_degrees=snapshot.direction_degrees,
        points=points,
    )