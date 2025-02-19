from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)

from project.automata_operations.automata_intersection import intersect_automata
from project.automata_operations.automaton_boolean_decomposition import (
    get_boolean_decomposition,
)


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
    (intersection_matrices, start_states, final_states) = intersect_automata(
        first, second
    )
    expected_dict = expected.to_dict()
    for expected_left_state in expected_dict.keys():
        for label in expected_dict[expected_left_state]:
            for expected_right_state in expected_dict[expected_left_state][label]:
                assert intersection_matrices[label].tocsr()[
                    expected_left_state.value, expected_right_state.value
                ]
    assert set(expected.start_states) == set(start_states)
    assert set(expected.final_states) == set(final_states)
