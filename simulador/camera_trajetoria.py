from __future__ import annotations

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

OUTPUT_PATH = Path(__file__).resolve().parent / "trajetoria_capturada.json"
from simulador.presentation.controller import SimulatorController


def main() -> None:
    controller = SimulatorController(output_path=OUTPUT_PATH)
    output_file, response = controller.run_camera_simulation()

    print()
    print(f"Trajetoria salva em: {output_file}")
    if response is None:
        print("Pontos insuficientes para calcular a trajetoria automatica. Capture mais movimento.")
        return

    print("Melhor janela de trajetoria:", response["selected_window"]["name"])
    print("Dias decorridos:", response["selected_window"]["elapsed_days"])
    print("Custo estimado:", round(response["metrics"]["window_cost"], 4))
    print("Probabilidade do estado escolhido:", round(response["metrics"]["best_probability"], 4))


if __name__ == "__main__":
    main()