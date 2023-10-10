import networkx as nx

from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    FiniteAutomaton,
)
from scipy.sparse import lil_array, lil_matrix

from project.graph_utils import get_graph_properties


def build_minimal_dfa_from_regex(regex_str: str) -> DeterministicFiniteAutomaton:
    regex = Regex(regex_str)
    epsilon_nfa = regex.to_epsilon_nfa()
    minimal_dfa = epsilon_nfa.minimize()
    return minimal_dfa


def build_nfa_from_graph(
    graph: nx.MultiDiGraph, start_vertices: set = None, end_vertices: set = None
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    if start_vertices is None:
        start_vertices = graph.nodes
    if end_vertices is None:
        end_vertices = graph.nodes

    for start_vertice in start_vertices:
        if not graph.has_node(start_vertice):
            raise Exception("Wrong start states")
    for end_vertice in end_vertices:
        if not graph.has_node(end_vertice):
            raise Exception("Wrong final states")

    for start_state in start_vertices:
        nfa.add_start_state(start_state)
    for end_state in end_vertices:
        nfa.add_final_state(end_state)

    return nfa


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
