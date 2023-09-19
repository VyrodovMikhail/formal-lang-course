import networkx as nx
import pytest

from project import graph_utils, automata_utils
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton


def build_nfa_from_graph(graph: nx.MultiDiGraph, start: set[int], end: set[int]):
    nfa = NondeterministicFiniteAutomaton()
    for edge in graph.edges(data=True):
        first, second, edge_data = edge
        nfa.add_transition(first, edge_data["label"], second)

    for start_state in start:
        nfa.add_start_state(start_state)
    for end_state in end:
        nfa.add_final_state(end_state)
    return nfa


def assert_nfa_info_equals_graph_info(
    nfa: NondeterministicFiniteAutomaton,
    graph: nx.MultiDiGraph,
    start_states: set,
    end_states: set,
):
    (
        expected_states_number,
        expected_transitions_number,
        expected_nfa_symbols,
    ) = graph_utils.get_graph_properties(graph)
    for state in start_states:
        assert state in nfa.start_states
    for state in end_states:
        assert nfa.is_final_state(state)
    assert expected_states_number == len(nfa.states)
    assert expected_transitions_number == nfa.get_number_transitions()
    assert expected_nfa_symbols["label"] == nfa.symbols


def test_build_nfa_from_labeled_two_cycles_graph():
    first_nodes_count = 5
    second_nodes_count = 10
    edge_labels = ("a", "b")
    name = "labeled_graph.dot"
    real_graph = graph_utils.create_labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, edge_labels, name
    )

    start_states = {1, 2, 3, 4}
    end_states = {5, 6, 7}
    expected_nfa = build_nfa_from_graph(real_graph, start_states, end_states)
    nfa = automata_utils.build_nfa_from_graph(real_graph, start_states, end_states)
    assert nfa.is_equivalent_to(expected_nfa)
    assert_nfa_info_equals_graph_info(nfa, real_graph, start_states, end_states)


def test_build_nfa_from_graph_from_name():
    real_graph = graph_utils.get_graph_from_name("bzip")

    start_states = {1, 2, 3, 4}
    end_states = {5, 6, 7}
    expected_nfa = build_nfa_from_graph(real_graph, start_states, end_states)
    nfa = automata_utils.build_nfa_from_graph(real_graph, start_states, end_states)
    assert nfa.is_equivalent_to(expected_nfa)
    assert_nfa_info_equals_graph_info(nfa, real_graph, start_states, end_states)


def test_build_nfa_without_start_or_final_vertices():
    first_nodes_count = 5
    second_nodes_count = 10
    edge_labels = ("a", "b")
    name = "labeled_graph.dot"
    real_graph = graph_utils.create_labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, edge_labels, name
    )

    start_states = set(real_graph.nodes)
    end_states = set(real_graph.nodes)
    expected_nfa = build_nfa_from_graph(real_graph, start_states, end_states)
    nfa = automata_utils.build_nfa_from_graph(real_graph)
    assert nfa.is_equivalent_to(expected_nfa)
    assert_nfa_info_equals_graph_info(nfa, real_graph, start_states, end_states)


def test_build_nfa_from_graph_exceptions():
    first_nodes_count = 5
    second_nodes_count = 10
    edge_labels = ("a", "b")
    name = "labeled_graph.dot"
    real_graph = graph_utils.create_labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, edge_labels, name
    )

    start_states = {1, 2, 3, 4, 20}
    end_states = {5, 6, 7}
    with pytest.raises(Exception, match="Wrong start states"):
        nfa = automata_utils.build_nfa_from_graph(real_graph, start_states, end_states)

    start_states = {1, 2, 3, 4}
    end_states = {5, 6, 7, 25}
    with pytest.raises(Exception, match="Wrong final states"):
        nfa = automata_utils.build_nfa_from_graph(real_graph, start_states, end_states)
