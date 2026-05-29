from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrajectoryPoint:
    x: int
    y: int
    timestamp: float


@dataclass(frozen=True)
class MotionSnapshot:
    speed_px_s: float
    direction_degrees: float


@dataclass(frozen=True)
class SimulationConfig:
    min_area: int = 900
    max_points: int = 128
    max_capture_seconds: float = 10.0
    max_idle_seconds: float = 2.0
    frame_sampling_interval_seconds: float = 0.5
    stop_on_idle: bool = False


@dataclass(frozen=True)
class CapturedTrajectory:
    captured_at: datetime
    total_distance_px: float
    speed_px_s: float
    direction_degrees: float
    points: list[TrajectoryPoint]


@dataclass(frozen=True)
class CaptureMetrics:
    total_distance_px: float
    tracked_points: int
    speed_px_s: float
    direction_degrees: float
    stop_reason: str