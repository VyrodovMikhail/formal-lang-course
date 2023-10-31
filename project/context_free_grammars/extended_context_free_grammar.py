from pathlib import Path
from typing import Dict, Union

from pyformlang.cfg import CFG, Terminal, Variable
from pyformlang.regular_expression import Regex


class ECFG:
    """Class for representation of extended context free grammar"""

    def __init__(
        self,
        terminals: set[str],
        nonterminals: set[str],
        start_symbol: str,
        productions: Dict[str, Regex],
    ):
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.start_symbol = start_symbol
        self.productions = productions

    @classmethod
    def ecfg_from_str(cls, grammar_str: str, start_symbol: str):
        productions_str = grammar_str.split("\n")
        productions = dict()
        terminals = set()
        nonterminals = set()
        for str_production in productions_str:
            if str_production == "":
                continue
            tokens = str_production.split()
            if len(tokens) < 3 or tokens[1] != "->":
                raise Exception("Wrong production syntax")
            nonterminals.add(tokens[0])

            for token in tokens[2:]:
                if token == "epsilon":
                    continue

                filtered_token_list = []
                i = 0
                while i < len(token) and token[i] in "[]*?()|+":
                    i += 1
                while i < len(token) and token[i] not in "[]*?()|+":
                    filtered_token_list.append(token[i])
                    i += 1
                if len(filtered_token_list) != 0:
                    filtered_token = "".join(filtered_token_list)
                    terminals.add(filtered_token)

            nonterminal = tokens[0]
            regex = Regex(" ".join(tokens[2:]))
            productions[nonterminal] = regex

        terminals -= nonterminals

        return ECFG(terminals, nonterminals, start_symbol, productions)

    @classmethod
    def ecfg_from_cfg_file(cls, path: Path, start_symbol: str) -> "ECFG":
        file = open(path, "r")
        grammar_str = file.read()
        file.close()

        cfg = CFG.from_text(grammar_str, start_symbol)

        return cls.ecfg_from_cfg_class(cfg)

    @classmethod
    def ecfg_from_cfg_class(cls, cfg: CFG) -> "ECFG":
        str_terminals = {terminal.value for terminal in cfg.terminals}
        str_variables = {variable.value for variable in cfg.variables}
        ecfg = cls(str_terminals, str_variables, cfg.start_symbol.value, dict())
        ecfg_productions = dict()

        for production in cfg.productions:
            str_body = [elem.value for elem in production.body]
            regex = Regex(" ".join(str_body))
            if production.head not in ecfg_productions:
                ecfg_productions[production.head.value] = regex
            else:
                ecfg_productions[production.head.value] = ecfg_productions[
                    production.head.value
                ].union(regex)

        return ecfg

    @classmethod
    def get_ecfg(cls, cfg: Union[CFG, Path], start_symbol: str):
        if isinstance(cfg, CFG):
            return cls.ecfg_from_cfg_class(cfg)
        elif isinstance(cfg, Path):
            return cls.ecfg_from_cfg_file(cfg, start_symbol)
