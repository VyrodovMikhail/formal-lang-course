from pathlib import Path
from pyformlang.cfg import CFG, Terminal, Variable, Production, Epsilon

from project.context_free_grammars.cfg_operations import (
    read_grammar_from_file,
    convert_cfg_to_wcnf,
    is_in_wcnf,
)


def test_is_in_wcnf():
    wcnf_grammar_productions = """
    S -> epsilon
    S -> A B
    A -> C S
    C -> c
    B -> b"""

    wcnf_grammar = CFG.from_text(wcnf_grammar_productions)
    assert is_in_wcnf(wcnf_grammar)

    not_wcnf_grammar_productions = """
    S -> A epsilon
    S -> A B C
    A -> C S
    C -> c q
    B -> b"""
    not_wcnf_grammar = CFG.from_text(not_wcnf_grammar_productions)
    assert not is_in_wcnf(not_wcnf_grammar)


def test_convert_cfg_to_wcnf():
    var_S = Variable("S")
    ter_a = Terminal("a")
    ter_b = Terminal("b")
    ter_c = Terminal("c")
    p0 = Production(var_S, [ter_a, ter_b, ter_c])

    cfg = CFG({var_S}, {ter_a, ter_b, ter_c}, var_S, {p0})
    wcnf_cfg = convert_cfg_to_wcnf(cfg)

    expected_productions = """
    S -> "VAR:a#CNF#" C#CNF#1
    C#CNF#1 -> "VAR:b#CNF#" "VAR:c#CNF#"
    c#CNF# -> c
    a#CNF# -> a
    b#CNF# -> b
    """
    expected_grammar = CFG.from_text(expected_productions)
    assert is_in_wcnf(wcnf_cfg)
    assert wcnf_cfg.productions == expected_grammar.productions

    p1 = Production(var_S, [Epsilon()])
    cfg = CFG({var_S}, set(), var_S, {p1})

    wcnf_cfg = convert_cfg_to_wcnf(cfg)

    expected_productions = "S -> epsilon"
    expected_grammar = CFG.from_text(expected_productions)

    assert is_in_wcnf(wcnf_cfg)
    assert not wcnf_cfg.is_normal_form()
    assert wcnf_cfg.productions == expected_grammar.productions


def test_read_grammar_from_file():
    expected_grammar = CFG.from_text(
        """
        S -> NP VP PUNC
        PUNC -> . | !
        VP -> V NP
        V -> buys | touches | sees
        NP -> georges | jacques | leo | Det N
        Det -> a | an | the
        N -> gorilla | dog | carrots"""
    )

    path_to_grammar = Path("tests/test_cfg_operations/grammar_in_file.txt")
    start_symbol = "S"
    real_grammar = read_grammar_from_file(path_to_grammar, start_symbol)
    assert real_grammar.productions == expected_grammar.productions
    assert real_grammar.start_symbol == expected_grammar.start_symbol
