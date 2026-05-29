from __future__ import annotations

from pathlib import Path

import cv2

from simulador.application.use_cases import CalculateTrajectoryFromCaptureUseCase, SaveCapturedTrajectoryUseCase
from simulador.domain.entities import CapturedTrajectory
from simulador.domain.services import build_captured_trajectory
from simulador.infrastructure.cv2_tracker import MotionTrajectoryTracker
from simulador.infrastructure.json_capture_repository import JsonCaptureRepository
from simulador.infrastructure.trajectory_gateway import QuantumTrajectoryGateway


class SimulatorController:
    def __init__(self, output_path: Path) -> None:
        repository = JsonCaptureRepository(output_path)
        self.output_path = output_path
        self.save_use_case = SaveCapturedTrajectoryUseCase(repository=repository)
        self.calculate_use_case = CalculateTrajectoryFromCaptureUseCase(
            repository=repository,
            calculator=QuantumTrajectoryGateway(),
        )

    def run_camera_simulation(self) -> tuple[Path, dict[str, object] | None]:
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            raise RuntimeError("Nao foi possivel acessar a camera do computador.")

        tracker = MotionTrajectoryTracker()

        try:
            while True:
                has_frame, frame = capture.read()
                if not has_frame:
                    raise RuntimeError("Falha ao ler frame da camera.")

                processed_frame, mask, center = tracker.process_frame(frame)
                metrics = tracker.capture_metrics()

                if center is not None:
                    print(
                        (
                            f"Centro detectado: x={center.x}, y={center.y}, "
                            f"distancia_total={metrics.total_distance_px:.2f} px, "
                            f"velocidade={metrics.speed_px_s:.2f} px/s, "
                            f"direcao={metrics.direction_degrees:.2f} graus"
                        ),
                        end="\r",
                        flush=True,
                    )

                cv2.imshow("Simulador de Trajetoria", processed_frame)
                cv2.imshow("Mascara de Movimento", mask)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if tracker.should_stop() and tracker.has_minimum_points():
                    print("\nParada automatica acionada. Encerrando captura e enviando para calculo...")
                    break
        finally:
            capture.release()
            cv2.destroyAllWindows()

        trajectory = self._build_trajectory(tracker)
        output_file = self.save_use_case.execute(trajectory)

        if not tracker.has_minimum_points():
            return output_file, None

        response = self.calculate_use_case.execute(output_file)
        return output_file, response

    def calculate_from_saved_capture(self, file_path: Path) -> dict[str, object]:
        return self.calculate_use_case.execute(file_path)

    def _build_trajectory(self, tracker: MotionTrajectoryTracker) -> CapturedTrajectory:
        return build_captured_trajectory(tracker.ordered_points(), tracker.last_snapshot)