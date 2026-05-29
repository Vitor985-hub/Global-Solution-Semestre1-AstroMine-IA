from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulador.presentation.controller import SimulatorController


DEFAULT_CAPTURE_FILE = Path(__file__).resolve().parent / "trajetoria_capturada.json"


def calculate_trajectory_from_capture(file_path: Path = DEFAULT_CAPTURE_FILE) -> dict[str, object]:
    controller = SimulatorController(output_path=DEFAULT_CAPTURE_FILE)
    return controller.calculate_from_saved_capture(file_path)


def main() -> None:
    response = calculate_trajectory_from_capture(DEFAULT_CAPTURE_FILE)

    print("Arquivo de captura:", DEFAULT_CAPTURE_FILE)
    print("Melhor janela de trajetoria:", response["selected_window"]["name"])
    print("Dias decorridos:", response["selected_window"]["elapsed_days"])
    print("Custo estimado:", round(response["metrics"]["window_cost"], 4))
    print("Probabilidade do estado escolhido:", round(response["metrics"]["best_probability"], 4))


if __name__ == "__main__":
    main()