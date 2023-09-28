from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.rpq_utils import rpq


def test_rpq():
    dfa = NondeterministicFiniteAutomaton()
    dfa.add_transitions(
        [(0, "a", 0), (0, "b", 0), (0, "c", 0), (0, "a", 1), (1, "b", 2)]
    )
    expected = {(0, 2), (0, 0)}

    graph = dfa.to_networkx()
    regex_str = "(a+b+c)*+(a b)"
    result = rpq(graph, regex_str, {0}, {2, 0})

    assert result == expected
