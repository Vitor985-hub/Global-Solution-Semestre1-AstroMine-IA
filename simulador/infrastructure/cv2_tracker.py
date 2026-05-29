from __future__ import annotations

from collections import deque
from pathlib import Path
import time

import cv2

from simulador.domain.entities import CaptureMetrics, MotionSnapshot, SimulationConfig, TrajectoryPoint
from simulador.domain.services import build_capture_metrics, build_motion_snapshot, describe_stop_reason, should_stop_capture


class MotionTrajectoryTracker:
    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=120,
            varThreshold=30,
            detectShadows=False,
        )
        self.points: deque[TrajectoryPoint] = deque(maxlen=self.config.max_points)
        self.last_snapshot = MotionSnapshot(speed_px_s=0.0, direction_degrees=0.0)
        self.started_at = time.time()
        self.last_motion_at: float | None = None
        self.last_sampled_at: float | None = None

    def process_frame(self, frame) -> tuple[object, object, TrajectoryPoint | None]:
        mask = self.background_subtractor.apply(frame)
        _, threshold = cv2.threshold(mask, 220, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
        cleaned = cv2.dilate(cleaned, kernel, iterations=2)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        moving_contours = [contour for contour in contours if cv2.contourArea(contour) >= self.config.min_area]

        center = None
        if moving_contours:
            contour = max(moving_contours, key=cv2.contourArea)
            x, y, width, height = cv2.boundingRect(contour)
            detected_at = time.time()
            center = TrajectoryPoint(x=x + width // 2, y=y + height // 2, timestamp=detected_at)
            self.last_motion_at = center.timestamp
            if self._should_sample_point(detected_at):
                previous = self.points[0] if self.points else None
                self.last_snapshot = build_motion_snapshot(center, previous)
                self.points.appendleft(center)
                self.last_sampled_at = detected_at
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 255), 2)
            cv2.circle(frame, (center.x, center.y), 6, (0, 0, 255), -1)

        self._draw_trajectory(frame)
        self._draw_metrics(frame)
        return frame, cleaned, center

    def should_stop(self) -> bool:
        return should_stop_capture(self.started_at, self.last_motion_at, time.time(), self.config)

    def _should_sample_point(self, detected_at: float) -> bool:
        if self.last_sampled_at is None:
            return True
        return (detected_at - self.last_sampled_at) >= self.config.frame_sampling_interval_seconds

    def stop_reason(self) -> str:
        return describe_stop_reason(self.started_at, self.last_motion_at, time.time(), self.config)

    def has_minimum_points(self, minimum_points: int = 3) -> bool:
        return len(self.points) >= minimum_points

    def ordered_points(self) -> list[TrajectoryPoint]:
        return list(reversed(self.points))

    def capture_metrics(self) -> CaptureMetrics:
        return build_capture_metrics(self.ordered_points(), self.last_snapshot, self.stop_reason())

    def _draw_trajectory(self, frame) -> None:
        previous_point = None
        for point in self.points:
            if previous_point is not None:
                cv2.line(frame, (previous_point.x, previous_point.y), (point.x, point.y), (255, 160, 0), 2)
            previous_point = point

    def _draw_metrics(self, frame) -> None:
        metrics = self.capture_metrics()
        cv2.putText(frame, f"Pontos rastreados: {metrics.tracked_points}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Trajetoria acumulada: {metrics.total_distance_px:.2f} px", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Velocidade: {metrics.speed_px_s:.2f} px/s", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Direcao: {metrics.direction_degrees:.2f} graus", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Captura: {metrics.stop_reason}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Amostragem fixa: {self.config.frame_sampling_interval_seconds:.1f}s", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Pressione q para encerrar antes", (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)