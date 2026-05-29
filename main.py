from __future__ import annotations

import argparse
from pathlib import Path

from simulador.presentation.controller import SimulatorController
from simulador.infrastructure.quantum_bridge import build_windows_from_capture_file
from trajetoria_asteroid.presentation.controller import TrajectoryController


ROOT_DIR = Path(__file__).resolve().parent
CAPTURE_FILE = ROOT_DIR / "simulador" / "trajetoria_capturada.json"
CAPTURE_PLOT_FILE = ROOT_DIR / "trajetoria_asteroid" / "grafico_trajeto_capturado.png"
CAPTURE_ANIMATION_FILE = ROOT_DIR / "trajetoria_asteroid" / "grafico_trajeto_capturado_animado.gif"


def run_quantum_demo() -> None:
    print("[1/3] Executando simulacao quantica de exemplo...")
    controller = TrajectoryController()
    response = controller.optimize_sample_trajectory()
    print("[2/3] Gerando grafico do exemplo...")
    graph_path = controller.plot_sample_trajectory()
    print("[3/3] Gerando animacao do exemplo...")
    animation_path = controller.animate_sample_trajectory()

    print("Melhor janela de trajetoria:", response["selected_window"]["name"])
    print("Dias decorridos:", response["selected_window"]["elapsed_days"])
    print("Custo estimado:", round(response["metrics"]["window_cost"], 4))
    print("Probabilidade do estado escolhido:", round(response["metrics"]["best_probability"], 4))
    print("Grafico salvo em:", graph_path)
    print("Animacao salva em:", animation_path)


def run_camera_flow() -> None:
    print("[1/4] Abrindo a camera e capturando a trajetoria no simulador...")
    simulator_controller = SimulatorController(output_path=CAPTURE_FILE)
    output_file, response = simulator_controller.run_camera_simulation()

    print()
    print(f"Trajetoria salva em: {output_file}")
    if response is None:
        print("Pontos insuficientes para calcular a trajetoria automatica. Capture mais movimento.")
        return

    print("[2/4] Convertendo a captura em janelas de trajetoria...")
    windows = build_windows_from_capture_file(output_file)
    trajectory_controller = TrajectoryController()
    print("[3/4] Gerando grafico da trajetoria capturada...")
    graph_path = trajectory_controller.plot_windows(windows, output_path=CAPTURE_PLOT_FILE)
    print("[4/4] Gerando animacao da trajetoria capturada...")
    animation_path = trajectory_controller.animate_windows(windows, output_path=CAPTURE_ANIMATION_FILE)

    print("Melhor janela de trajetoria:", response["selected_window"]["name"])
    print("Dias decorridos:", response["selected_window"]["elapsed_days"])
    print("Custo estimado:", round(response["metrics"]["window_cost"], 4))
    print("Probabilidade do estado escolhido:", round(response["metrics"]["best_probability"], 4))
    print("Grafico da captura salvo em:", graph_path)
    print("Animacao da captura salva em:", animation_path)


def run_from_saved_capture() -> None:
    print("[1/3] Carregando a captura salva do simulador...")
    simulator_controller = SimulatorController(output_path=CAPTURE_FILE)
    response = simulator_controller.calculate_from_saved_capture(CAPTURE_FILE)
    print("[2/3] Convertendo a captura em grafico...")
    windows = build_windows_from_capture_file(CAPTURE_FILE)
    trajectory_controller = TrajectoryController()
    graph_path = trajectory_controller.plot_windows(windows, output_path=CAPTURE_PLOT_FILE)
    print("[3/3] Gerando animacao da captura...")
    animation_path = trajectory_controller.animate_windows(windows, output_path=CAPTURE_ANIMATION_FILE)

    print("Arquivo de captura:", CAPTURE_FILE)
    print("Melhor janela de trajetoria:", response["selected_window"]["name"])
    print("Dias decorridos:", response["selected_window"]["elapsed_days"])
    print("Custo estimado:", round(response["metrics"]["window_cost"], 4))
    print("Probabilidade do estado escolhido:", round(response["metrics"]["best_probability"], 4))
    print("Grafico da captura salvo em:", graph_path)
    print("Animacao da captura salva em:", animation_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ponto unico de entrada do sistema AstroMine IA")
    parser.add_argument(
        "mode",
        nargs="?",
        default="simulador",
        choices=["simulador", "captura", "grafico"],
        help="simulador: abre a camera, captura a trajetoria e envia para as simulacoes seguintes; captura: reutiliza a captura salva; grafico: executa so o exemplo quantico",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.mode == "simulador":
        run_camera_flow()
        return

    if args.mode == "captura":
        run_from_saved_capture()
        return

    run_quantum_demo()


if __name__ == "__main__":
    main()