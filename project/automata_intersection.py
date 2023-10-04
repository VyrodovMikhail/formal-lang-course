from typing import Tuple

from pyformlang.finite_automaton import FiniteAutomaton
from scipy.sparse import lil_array, lil_matrix, kron

from project.graph_utils import get_graph_properties


def get_boolean_decomposition(automaton: FiniteAutomaton) -> dict[lil_matrix]:
    graph = automaton.to_networkx()
    nodes_number, edges_number, labels = get_graph_properties(graph)
    states_count = len(automaton.states)
    boolean_decomposition = {}
    for label in labels["label"]:
        boolean_decomposition[label] = lil_array(
            (states_count, states_count), dtype=bool
        )
    states_dict = dict(
        [(state, index) for (index, state) in enumerate(automaton.states)]
    )

    for start, transitions in automaton.to_dict().items():
        for label, end_states in transitions.items():
            if not isinstance(end_states, set):
                end_states = {end_states}

            for state in end_states:
                first_index = states_dict[start]
                second_index = states_dict[state]

                boolean_decomposition[label][first_index, second_index] = True

    return boolean_decomposition


def intersect_automata(
    first: FiniteAutomaton, second: FiniteAutomaton
) -> Tuple[dict[lil_matrix], list[int], list[int]]:
    first_boolean_decomposition = get_boolean_decomposition(first)
    second_boolean_decomposition = get_boolean_decomposition(second)

    intersection_labels = set(first_boolean_decomposition.keys()).intersection(
        set(second_boolean_decomposition.keys())
    )
    intersection_matrices = dict()
    start_states = list()
    final_states = list()

    for label in intersection_labels:
        intersection_matrices[label] = kron(
            first_boolean_decomposition[label], second_boolean_decomposition[label]
        )

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
