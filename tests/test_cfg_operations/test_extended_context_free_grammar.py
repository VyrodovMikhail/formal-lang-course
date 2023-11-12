import pytest

from pathlib import Path
from pyformlang.cfg import CFG

from project.context_free_grammars.extended_context_free_grammar import ECFG


def test_ecfg_from_cfg_class():
    cfg_str = """
    S -> NP VP PUNC
    PUNC -> A | B
    VP -> V NP
    NP -> georges | jacques | leo | Det N"""

    cfg = CFG.from_text(cfg_str, "S")

    ecfg = ECFG.ecfg_from_cfg_class(cfg)

    str_terminals = {terminal.value for terminal in cfg.terminals}
    str_variables = {variable.value for variable in cfg.variables}

    assert ecfg.terminals == str_terminals
    assert ecfg.nonterminals == str_variables
    assert ecfg.start_symbol == cfg.start_symbol.value


def test_ecfg_from_str():
    ecfg_str = """
    S -> A | b* S
    A -> a* b c"""

    ecfg = ECFG.ecfg_from_str(ecfg_str, "S")

    assert ecfg.terminals == {"b", "c", "a"}
    assert ecfg.nonterminals == {"S", "A"}
    assert ecfg.start_symbol == "S"

    ecfg_str = """
        S ->
        A -> a* b c"""

    with pytest.raises(Exception, match="Wrong production syntax"):
        ecfg = ECFG.ecfg_from_str(ecfg_str, "S")

    ecfg_str = """
            S
            A -> a* b c"""

    with pytest.raises(Exception, match="Wrong production syntax"):
        ecfg = ECFG.ecfg_from_str(ecfg_str, "S")


def test_ecfg_from_cfg_file():
    path_to_grammar = Path("tests/test_cfg_operations/simple_cfg_grammar.txt")
    ecfg = ECFG.ecfg_from_cfg_file(path_to_grammar, "S")

    cfg_str = """
    S -> A | B | epsilon
    A -> a
    B -> b c d"""

    cfg = CFG.from_text(cfg_str, "S")

    str_terminals = {terminal.value for terminal in cfg.terminals}
    str_variables = {variable.value for variable in cfg.variables}

    assert ecfg.terminals == str_terminals
    assert ecfg.nonterminals == str_variables
    assert ecfg.start_symbol == cfg.start_symbol.value
