from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)

from project.automata_intersection import get_boolean_decomposition, intersect_automata


def test_get_boolean_decomposition():
    dfa = DeterministicFiniteAutomaton()

    dfa.add_transition(1, "b", 1)
    dfa.add_transition(1, "a", 0)
    dfa.add_transition(0, "c", 0)
    dfa.add_transition(0, "a", 1)

    decomposition = get_boolean_decomposition(dfa)

    expected = dict()
    expected["a"] = [[0, 1], [1, 0]]
    expected["b"] = [[0, 0], [0, 1]]
    expected["c"] = [[1, 0], [0, 0]]

    for key in expected.keys():
        for i in range(len(expected[key])):
            for k in range(len(expected[key])):
                assert expected[key][i][k] == decomposition[key][i, k]


def test_intersect_automata():
    first = DeterministicFiniteAutomaton()

    first.add_transitions([(0, "a", 0), (0, "b", 1), (1, "c", 1), (1, "b", 0)])

    first.add_start_state(0)
    first.add_final_state(1)

    second = NondeterministicFiniteAutomaton()

    second.add_transitions([(0, "a", 0), (0, "a", 1), (1, "b", 1), (1, "c", 1)])

    second.add_start_state(0)
    second.add_final_state(1)

    expected = NondeterministicFiniteAutomaton()

    expected.add_transitions(
        [(0, "a", 0), (0, "a", 1), (1, "b", 3), (3, "b", 1), (3, "c", 3)]
    )

    expected.add_start_state(0)
    expected.add_final_state(3)

    assert expected == intersect_automata(first, second)
