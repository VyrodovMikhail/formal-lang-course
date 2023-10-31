from pathlib import Path
from pyformlang.cfg import CFG, Terminal, Variable


def convert_cfg_to_wcnf(grammar: CFG) -> CFG:
    weak_grammar = grammar.eliminate_unit_productions().remove_useless_symbols()
    decomposed_productions = weak_grammar._get_productions_with_only_single_terminals()
    new_productions = weak_grammar._decompose_productions(decomposed_productions)
    return CFG(start_symbol=weak_grammar.start_symbol, productions=set(new_productions))


def is_in_wcnf(grammar: CFG) -> bool:
    for production in grammar.productions:
        if len(production.body) > 2:
            return False

        for symbol in production.body:
            if len(production.body) > 1 and type(symbol) is not Variable:
                return False
            if len(production.body) == 1 and type(symbol) is Variable:
                return False

    return True


def read_grammar_from_file(path: Path, start_symbol: str = "S") -> CFG:
    file = open(path, "r")
    grammar_text = file.read()
    return CFG.from_text(grammar_text, Variable(start_symbol))
