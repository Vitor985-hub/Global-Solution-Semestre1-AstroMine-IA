from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from simulador.application.ports import CaptureRepository
from simulador.domain.entities import CapturedTrajectory, TrajectoryPoint


class JsonCaptureRepository(CaptureRepository):
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def save(self, trajectory: CapturedTrajectory) -> Path:
        payload = {
            "captured_at": trajectory.captured_at.isoformat(),
            "total_distance_px": trajectory.total_distance_px,
            "speed_px_s": trajectory.speed_px_s,
            "direction_degrees": trajectory.direction_degrees,
            "points": [
                {
                    "x": point.x,
                    "y": point.y,
                    "timestamp": point.timestamp,
                }
                for point in trajectory.points
            ],
        }
        self.output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.output_path

    def load(self, file_path: Path) -> CapturedTrajectory:
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo de captura nao encontrado: {file_path}")

        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return CapturedTrajectory(
            captured_at=datetime.fromisoformat(payload["captured_at"]),
            total_distance_px=float(payload["total_distance_px"]),
            speed_px_s=float(payload["speed_px_s"]),
            direction_degrees=float(payload["direction_degrees"]),
            points=[
                TrajectoryPoint(
                    x=int(point["x"]),
                    y=int(point["y"]),
                    timestamp=float(point["timestamp"]),
                )
                for point in payload["points"]
            ],
        )