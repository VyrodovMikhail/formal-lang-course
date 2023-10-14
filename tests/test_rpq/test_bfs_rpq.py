import networkx as nx

from pyformlang.finite_automaton import DeterministicFiniteAutomaton

from project.automata_operations.automaton_boolean_decomposition import (
    get_boolean_decomposition,
)
from project.rpq.bfs_rpq import construct_direct_sums_matrices, bfs_rpq
from project.rpq.bfs_rpq_mode import BfsRpqMode


def test_construct_direct_sums_matrices():
    first_dfa = DeterministicFiniteAutomaton()

    first_dfa.add_transition(1, "b", 0)
    first_dfa.add_transition(1, "a", 0)
    first_dfa.add_transition(0, "c", 1)
    first_dfa.add_transition(0, "a", 1)

    first_decomposition = get_boolean_decomposition(first_dfa)

    second_dfa = DeterministicFiniteAutomaton()

    second_dfa.add_transition(1, "b", 1)
    second_dfa.add_transition(1, "a", 0)
    second_dfa.add_transition(0, "c", 0)
    second_dfa.add_transition(0, "a", 1)

    second_decomposition = get_boolean_decomposition(second_dfa)

    expected_direct_sums = dict()

    expected_direct_sums["a"] = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]

    expected_direct_sums["b"] = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]]

    expected_direct_sums["c"] = [[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]

    direct_sums = construct_direct_sums_matrices(
        first_decomposition, second_decomposition
    )

    for key in expected_direct_sums.keys():
        for i in range(len(expected_direct_sums[key])):
            for k in range(len(expected_direct_sums[key])):
                assert direct_sums[key][i, k] == expected_direct_sums[key][i][k]


def test_bfs_rpq():
    # Test case was taken from https://github.com/FormalLanguageConstrainedPathQuerying/FormalLanguageConstrainedReachability-LectureNotes
    regex = "b*.a.b"
    graph = nx.MultiDiGraph()
    nodes = [0, 1, 2, 3]
    edges = [
        (nodes[0], nodes[1], {"label": "a"}),
        (nodes[0], nodes[3], {"label": "b"}),
        (nodes[3], nodes[0], {"label": "b"}),
        (nodes[1], nodes[2], {"label": "b"}),
        (nodes[2], nodes[0], {"label": "a"}),
    ]
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    result_vertices = bfs_rpq(
        graph, regex, {nodes[0]}, {nodes[2]}, BfsRpqMode.RPQ_FOR_VERTICES_SET
    )
    assert result_vertices == {nodes[2]}

    result_vertices = bfs_rpq(
        graph, regex, {nodes[0]}, {nodes[2]}, BfsRpqMode.RPQ_FOR_EVERY_VERTEX
    )
    assert result_vertices == {(nodes[0], nodes[2])}


def test_bfs_rpq_for_every_vertice():
    regex = "(a*)|(b*)|(c*)"
    graph = nx.MultiDiGraph()
    nodes = [0, 1, 2, 3]
    edges = [
        (nodes[0], nodes[1], {"label": "a"}),
        (nodes[1], nodes[2], {"label": "a"}),
        (nodes[3], nodes[0], {"label": "a"}),
        (nodes[2], nodes[1], {"label": "b"}),
        (nodes[2], nodes[3], {"label": "c"}),
    ]
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    result_vertices = bfs_rpq(
        graph,
        regex,
        {nodes[0], nodes[1]},
        {nodes[2], nodes[3]},
        BfsRpqMode.RPQ_FOR_EVERY_VERTEX,
    )
    assert result_vertices == {(nodes[0], nodes[2]), (nodes[1], nodes[2])}

    result_vertices = bfs_rpq(
        graph, regex, {nodes[0]}, {nodes[2]}, BfsRpqMode.RPQ_FOR_EVERY_VERTEX
    )
    assert result_vertices == {(nodes[0], nodes[2])}
