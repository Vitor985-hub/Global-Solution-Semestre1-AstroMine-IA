from __future__ import annotations

from typing import Sequence

from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import SparsePauliOp

from trajetoria_asteroid.application.ports import TrajectoryOptimizer
from trajetoria_asteroid.domain.entities import OptimizationResult, OptimizationWeights, TrajectoryWindow
from trajetoria_asteroid.domain.services import build_qubo_coefficients, build_window_cost

try:
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
except ImportError:  # pragma: no cover - depends on optional runtime package
    QAOA = None
    COBYLA = None


class QiskitTrajectoryOptimizer(TrajectoryOptimizer):
    def optimize(
        self,
        windows: Sequence[TrajectoryWindow],
        weights: OptimizationWeights,
        reps: int = 2,
    ) -> OptimizationResult:
        if QAOA is None or COBYLA is None:
            raise ImportError("Instale qiskit-algorithms para executar o QAOA.")

        linear, quadratic = build_qubo_coefficients(windows, weights)
        operator, offset = qubo_to_ising(linear, quadratic)

        qaoa = QAOA(sampler=StatevectorSampler(), optimizer=COBYLA(maxiter=150), reps=reps)
        result = qaoa.compute_minimum_eigenvalue(operator)
        best_bitstring, best_probability = extract_best_bitstring(result)
        selected_window = decode_bitstring(best_bitstring, windows, weights)

        return OptimizationResult(
            selected_window=selected_window,
            offset=offset,
            best_probability=best_probability,
            window_cost=build_window_cost(selected_window, weights),
        )


def qubo_to_ising(
    linear: Sequence[float],
    quadratic: dict[tuple[int, int], float],
) -> tuple[SparsePauliOp, float]:
    num_qubits = len(linear)
    pauli_terms: dict[str, float] = {}
    offset = 0.0

    def add_term(label: str, value: float) -> None:
        pauli_terms[label] = pauli_terms.get(label, 0.0) + value

    for index, coeff in enumerate(linear):
        offset += coeff / 2.0
        label = ["I"] * num_qubits
        label[index] = "Z"
        add_term("".join(label), -coeff / 2.0)

    for (left, right), coeff in quadratic.items():
        offset += coeff / 4.0

        left_label = ["I"] * num_qubits
        left_label[left] = "Z"
        add_term("".join(left_label), -coeff / 4.0)

        right_label = ["I"] * num_qubits
        right_label[right] = "Z"
        add_term("".join(right_label), -coeff / 4.0)

        pair_label = ["I"] * num_qubits
        pair_label[left] = "Z"
        pair_label[right] = "Z"
        add_term("".join(pair_label), coeff / 4.0)

    return SparsePauliOp.from_list(list(pauli_terms.items())), offset


def decode_bitstring(
    bitstring: str,
    windows: Sequence[TrajectoryWindow],
    weights: OptimizationWeights,
) -> TrajectoryWindow:
    selected_indexes = [index for index, bit in enumerate(bitstring[::-1]) if bit == "1"]

    if not selected_indexes:
        return min(windows, key=lambda window: build_window_cost(window, weights))

    if len(selected_indexes) == 1:
        return windows[selected_indexes[0]]

    selected_windows = [windows[index] for index in selected_indexes]
    return min(selected_windows, key=lambda window: build_window_cost(window, weights))


def extract_best_bitstring(result: object) -> tuple[str, float]:
    best_measurement = getattr(result, "best_measurement", None)
    if best_measurement:
        return best_measurement["bitstring"], float(best_measurement["probability"])

    eigenstate = getattr(result, "eigenstate", None)
    if isinstance(eigenstate, dict):
        best_bitstring = max(eigenstate, key=eigenstate.get)
        return best_bitstring, float(eigenstate[best_bitstring])

    if hasattr(eigenstate, "binary_probabilities"):
        probabilities = eigenstate.binary_probabilities()
        best_bitstring = max(probabilities, key=probabilities.get)
        return best_bitstring, float(probabilities[best_bitstring])

    raise TypeError("Nao foi possivel extrair o melhor bitstring do resultado do QAOA.")