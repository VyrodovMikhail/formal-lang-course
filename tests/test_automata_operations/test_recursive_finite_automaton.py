from pathlib import Path
from pyformlang.cfg import CFG

from project.context_free_grammars.extended_context_free_grammar import ECFG
from project.automata_operations.recursive_finite_automaton import RFA


def test_rfa_from_ecfg():
    ecfg_str = """
        S -> A | b* S
        A -> a* b c"""

    ecfg = ECFG.ecfg_from_str(ecfg_str, "S")

    rfa = RFA.rfa_from_ecfg(ecfg, "S")

    assert rfa.terminals == {"b", "c", "a"}
    assert rfa.nonterminals == {"S", "A"}
    assert rfa.start_symbol == "S"


def test_rfa_from_ecfg_str():
    ecfg_str = """
        S -> A | b* S
        A -> a* b c"""

    rfa = RFA.rfa_from_ecfg(ecfg_str, "S")

    assert rfa.terminals == {"b", "c", "a"}
    assert rfa.nonterminals == {"S", "A"}
    assert rfa.start_symbol == "S"


def test_rfa_from_cfg_class():
    cfg_str = """
        S -> NP VP PUNC
        PUNC -> A | B
        VP -> V NP
        NP -> georges | jacques | leo | Det N"""

    cfg = CFG.from_text(cfg_str, "S")

    rfa = RFA.rfa_from_ecfg(cfg, "S")

    str_terminals = {terminal.value for terminal in cfg.terminals}
    str_variables = {variable.value for variable in cfg.variables}

    assert rfa.terminals == str_terminals
    assert rfa.nonterminals == str_variables
    assert rfa.start_symbol == cfg.start_symbol.value


def test_rfa_from_cfg_file():
    path_to_grammar = Path("tests/test_cfg_operations/simple_cfg_grammar.txt")
    cfg_str = """
        S -> A | B | epsilon
        A -> a
        B -> b c d"""

    cfg = CFG.from_text(cfg_str, "S")

    rfa = RFA.rfa_from_ecfg(path_to_grammar, "S")

    str_terminals = {terminal.value for terminal in cfg.terminals}
    str_variables = {variable.value for variable in cfg.variables}

    assert rfa.terminals == str_terminals
    assert rfa.nonterminals == str_variables
    assert rfa.start_symbol == cfg.start_symbol.value


def test_minimize():
    ecfg_str = """
        S -> A | b* S
        A -> a* b c"""

    rfa = RFA.rfa_from_ecfg(ecfg_str, "S")

    minimized_rfa = RFA.rfa_from_ecfg(ecfg_str, "S")
    minimized_rfa.minimize()

    for nonterminal in rfa.automata:
        automaton = rfa.automata[nonterminal]
        minimized_automaton = minimized_rfa.automata[nonterminal]
        assert minimized_automaton.is_equivalent_to(automaton)
