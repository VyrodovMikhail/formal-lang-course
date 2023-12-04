from pathlib import Path
from typing import Dict, Union

from scipy.sparse import lil_array, lil_matrix
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import FiniteAutomaton, State

from project.context_free_grammars.extended_context_free_grammar import ECFG
from project.automata_operations.automaton_boolean_decomposition import (
    make_state_indices_dict,
)


class RFA:
    """Class for representation of recursive finite automaton"""

    def __init__(
        self,
        terminals: set[str],
        nonterminals: set[str],
        start_symbol: str,
        automata: Dict[str, FiniteAutomaton],
    ):
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.start_symbol = start_symbol
        self.automata = automata

    @classmethod
    def rfa_from_ecfg(
        cls, ecfg: Union[ECFG, CFG, str, Path], start_symbol: str = "S"
    ) -> "RFA":
        real_ecfg = None
        if isinstance(ecfg, CFG):
            real_ecfg = ECFG.ecfg_from_cfg_class(ecfg)
        elif isinstance(ecfg, str):
            real_ecfg = ECFG.ecfg_from_str(ecfg, start_symbol)
        elif isinstance(ecfg, Path):
            real_ecfg = ECFG.ecfg_from_cfg_file(ecfg, start_symbol)
        elif isinstance(ecfg, ECFG):
            real_ecfg = ecfg

        automata = dict()
        for nonterminal in real_ecfg.productions:
            regex = real_ecfg.productions[nonterminal]
            automata[nonterminal] = regex.to_epsilon_nfa()

        return RFA(
            real_ecfg.terminals,
            real_ecfg.nonterminals,
            real_ecfg.start_symbol,
            automata,
        )

    def minimize(self):
        for nonterminal, automaton in self.automata.items():
            self.automata[nonterminal] = automaton.minimize()

    def get_states(self):
        states, start_states, final_states = set(), set(), set()
        for nonterminal, automaton in self.automata.items():
            for state in automaton.states:
                new_state = State((nonterminal, state.value))
                states.add(new_state)

                if state in automaton.start_states:
                    start_states.add(new_state)
                if state in automaton.final_states:
                    final_states.add(new_state)

        return states, start_states, final_states

    def get_binary_decomposition(self):
        boolean_decomposition = {}
        states, start_states, final_states = self.get_states()

        states_dict = make_state_indices_dict(states)

        for nonterminal, automaton in self.automata.items():
            for start, transitions in automaton.to_dict().items():
                for label, end_states in transitions.items():
                    if not isinstance(end_states, set):
                        end_states = {end_states}

                    if label not in boolean_decomposition:
                        boolean_decomposition[label] = lil_array(
                            (len(states), len(states)), dtype=bool
                        )

                    for state in end_states:
                        first_index = states_dict[State((nonterminal, start.value))]
                        second_index = states_dict[State((nonterminal, state.value))]

                        boolean_decomposition[label][first_index, second_index] = True

        return boolean_decomposition
