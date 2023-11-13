from pathlib import Path

import networkx as nx

from pyformlang.cfg import CFG, Terminal, Variable, Production
from project.cfpq.hellings import hellings, start_hellings


def test_hellings():
    # Test case from https://github.com/FormalLanguageConstrainedPathQuerying/FormalLanguageConstrainedReachability-LectureNotes is used
    vertices = [0, 1, 2, 3]
    edges = [
        (0, 1, {"label": "a"}),
        (2, 0, {"label": "a"}),
        (1, 2, {"label": "a"}),
        (2, 3, {"label": "b"}),
        (3, 2, {"label": "b"}),
    ]

    graph = nx.MultiDiGraph()
    graph.add_edges_from(edges)
    graph.add_nodes_from(vertices)

    var_S = Variable("S")
    var_S1 = Variable("S1")
    var_A = Variable("A")
    var_B = Variable("B")

    ter_a = Terminal("a")
    ter_b = Terminal("b")

    p0 = Production(var_S, [var_A, var_B])
    p1 = Production(var_S, [var_A, var_S1])
    p2 = Production(var_S1, [var_S, var_B])
    p3 = Production(var_A, [ter_a])
    p4 = Production(var_B, [ter_b])

    grammar = CFG(
        {var_S, var_S1, var_A, var_B}, {ter_a, ter_b}, var_S, [p0, p1, p2, p3, p4]
    )

    expected_result = {
        (var_A, 2, 0),
        (var_A, 1, 2),
        (var_S, 1, 2),
        (var_S1, 2, 3),
        (var_B, 3, 2),
        (var_S, 0, 2),
        (var_S1, 0, 2),
        (var_S, 1, 3),
        (var_S1, 1, 2),
        (var_S, 2, 2),
        (var_A, 0, 1),
        (var_B, 2, 3),
        (var_S, 2, 3),
        (var_S1, 2, 2),
        (var_S, 0, 3),
        (var_S1, 0, 3),
        (var_S1, 1, 3),
    }

    result = hellings(grammar, graph)
    assert result == expected_result

    expected_result = {
        (var_A, 1, 2),
        (var_S, 1, 2),
        (var_S, 0, 2),
        (var_S1, 0, 2),
        (var_S, 1, 3),
        (var_S1, 1, 2),
        (var_A, 0, 1),
        (var_S, 0, 3),
        (var_S1, 0, 3),
        (var_S1, 1, 3),
    }

    result_with_start_set = hellings(grammar, graph, {0, 1})
    assert result_with_start_set == expected_result

    expected_result = {
        (var_A, 1, 2),
        (var_S, 1, 2),
        (var_S, 0, 2),
        (var_S1, 0, 2),
        (var_S1, 1, 2),
    }

    result_with_end_set = hellings(grammar, graph, {0, 1}, {2})
    assert result_with_end_set == expected_result

    expected_result = {
        (var_S1, 0, 2),
        (var_S1, 1, 2),
    }

    result_with_nonterminal = hellings(grammar, graph, {0, 1}, {2}, var_S1)
    assert result_with_nonterminal == expected_result


def test_hellings_from_files():
    var_S = Variable("S")
    var_S1 = Variable("S1")
    var_A = Variable("A")
    var_B = Variable("B")

    expected_result = {
        (var_A, "2", "0"),
        (var_A, "1", "2"),
        (var_S, "1", "2"),
        (var_S1, "2", "3"),
        (var_B, "3", "2"),
        (var_S, "0", "2"),
        (var_S1, "0", "2"),
        (var_S, "1", "3"),
        (var_S1, "1", "2"),
        (var_S, "2", "2"),
        (var_A, "0", "1"),
        (var_B, "2", "3"),
        (var_S, "2", "3"),
        (var_S1, "2", "2"),
        (var_S, "0", "3"),
        (var_S1, "0", "3"),
        (var_S1, "1", "3"),
    }
    path = Path("tests/test_cfpq/grammar.txt")

    result = start_hellings(path, "S", "tests/test_cfpq/graph.dot")
    assert result == expected_result
