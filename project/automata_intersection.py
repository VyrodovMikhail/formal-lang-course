from pyformlang.finite_automaton import FiniteAutomaton, NondeterministicFiniteAutomaton
from scipy.sparse import find, lil_array, lil_matrix, kron

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


def intersect_automata(first: FiniteAutomaton, second: FiniteAutomaton):
    first_boolean_decomposition = get_boolean_decomposition(first)
    second_boolean_decomposition = get_boolean_decomposition(second)

    intersection_labels = set(first_boolean_decomposition.keys()).intersection(
        set(second_boolean_decomposition.keys())
    )
    intersection_matrices = dict()

    result_automaton = NondeterministicFiniteAutomaton()
    for label in intersection_labels:
        intersection_matrices[label] = kron(
            first_boolean_decomposition[label], second_boolean_decomposition[label]
        )

    for label, intersection_matrix in intersection_matrices.items():
        edges = find(intersection_matrix)
        rows_indexes, columns_indexes, real_labels = edges
        for (first_in_edge, second_in_edge, _) in zip(
            rows_indexes, columns_indexes, real_labels
        ):
            result_automaton.add_transition(first_in_edge, label, second_in_edge)

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
            result_automaton.add_start_state(i * len(second_states) + j)

    for i in first_final_indices:
        for j in second_final_indices:
            result_automaton.add_final_state(i * len(second_states) + j)

    return result_automaton
