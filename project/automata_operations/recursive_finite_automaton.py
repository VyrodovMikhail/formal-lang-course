from pathlib import Path
from typing import Dict, Union

from pyformlang.cfg import CFG
from pyformlang.finite_automaton import FiniteAutomaton

from project.context_free_grammars.extended_context_free_grammar import ECFG


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
        cls, ecfg: Union[ECFG, CFG, str, Path], start_symbol: str
    ) -> "RFA":
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
