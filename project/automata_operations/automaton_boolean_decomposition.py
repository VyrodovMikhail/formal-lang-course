from pyformlang.finite_automaton import FiniteAutomaton
from scipy.sparse import lil_array, lil_matrix

from project.graph_utils import get_graph_properties


def make_state_indices_dict(states: set):
    states_dict = dict([(state, index) for (index, state) in enumerate(states)])

    return states_dict


def get_boolean_decomposition(automaton: FiniteAutomaton) -> dict[lil_matrix]:
    graph = automaton.to_networkx()
    nodes_number, edges_number, labels = get_graph_properties(graph)
    states_count = len(automaton.states)
    boolean_decomposition = {}
    for label in labels["label"]:
        boolean_decomposition[label] = lil_array(
            (states_count, states_count), dtype=bool
        )
    states_dict = make_state_indices_dict(automaton.states)

    for start, transitions in automaton.to_dict().items():
        for label, end_states in transitions.items():
            if not isinstance(end_states, set):
                end_states = {end_states}

            for state in end_states:
                first_index = states_dict[start]
                second_index = states_dict[state]

                boolean_decomposition[label][first_index, second_index] = True

    return boolean_decomposition
