from pyformlang.finite_automaton import FiniteAutomaton, State
from scipy.sparse import lil_matrix, kron

from project.automata_operations.automaton_boolean_decomposition import (
    get_boolean_decomposition,
)
from project.matrix_operations import (
    intersect_boolean_decompositions,
)


def intersect_automata(
    first: FiniteAutomaton, second: FiniteAutomaton
) -> tuple[dict[lil_matrix], list[int], list[int]]:
    first_boolean_decomposition = get_boolean_decomposition(first)
    second_boolean_decomposition = get_boolean_decomposition(second)

    intersection_matrices = intersect_boolean_decompositions(
        first_boolean_decomposition, second_boolean_decomposition
    )
    start_states = list()
    final_states = list()

    first_states = list(first.states)
    second_states = list(second.states)

    first_start_indices = []
    first_final_indices = []
    for i in range(len(first_states)):
        if first_states[i] in first.start_states:
            first_start_indices.append(i)
        if first_states[i] in first.final_states:
            first_final_indices.append(i)

    second_start_indices = []
    second_final_indices = []
    for i in range(len(second_states)):
        if second_states[i] in second.start_states:
            second_start_indices.append(i)
        if second_states[i] in second.final_states:
            second_final_indices.append(i)

    for i in first_start_indices:
        for j in second_start_indices:
            start_states.append(i * len(second_states) + j)

    for i in first_final_indices:
        for j in second_final_indices:
            final_states.append(i * len(second_states) + j)

    return intersection_matrices, start_states, final_states
