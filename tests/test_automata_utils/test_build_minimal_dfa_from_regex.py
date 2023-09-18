from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from project import automata_utils


def test_build_minimal_dfa_from_regex():
    regex_str = "(a+b+c)*+(a b)"
    min_dfa = automata_utils.build_minimal_dfa_from_regex(regex_str)
    expected = NondeterministicFiniteAutomaton()
    expected.add_start_state(0)
    expected.add_final_state(2)
    expected.add_final_state(0)
    expected.add_transitions(
        [(0, "a", 0), (0, "b", 0), (0, "c", 0), (0, "a", 1), (1, "b", 2)]
    )
    assert min_dfa.is_deterministic()
    assert expected.is_equivalent_to(min_dfa)
