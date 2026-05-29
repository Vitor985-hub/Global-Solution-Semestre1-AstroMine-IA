from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trajetoria_asteroid.presentation.controller import TrajectoryController


def main() -> None:
    controller = TrajectoryController()
    response = controller.optimize_sample_trajectory()
    graph_path = controller.plot_sample_trajectory()
    animation_path = controller.animate_sample_trajectory()

    print("Melhor janela de trajetoria:", response["selected_window"]["name"])
    print("Dias decorridos:", response["selected_window"]["elapsed_days"])
    print("Custo estimado:", round(response["metrics"]["window_cost"], 4))
    print("Probabilidade do estado escolhido:", round(response["metrics"]["best_probability"], 4))
    print("Grafico salvo em:", graph_path)
    print("Animacao salva em:", animation_path)


if __name__ == "__main__":
    main()