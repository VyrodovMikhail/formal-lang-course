from typing import Union
from pathlib import Path

import networkx as nx
from pyformlang.cfg import CFG, Terminal, Epsilon
from scipy.sparse import lil_array

from project.context_free_grammars.cfg_operations import (
    convert_cfg_to_wcnf,
    is_in_wcnf,
    read_grammar_from_file,
)
from project.graph_utils import read_from_dot


def start_matrix_algo(
    grammar: Union[Path, CFG],
    start_symbol: str,
    graph: Union[str, nx.MultiDiGraph],
    start=None,
    end=None,
):
    if isinstance(grammar, Path):
        grammar = read_grammar_from_file(grammar, start_symbol)

    if isinstance(graph, str):
        graph = read_from_dot(graph)

    return matrix_algo(grammar, graph, start, end)


def get_grammar_helping_info(grammar: CFG):
    symbol_dict = dict()
    epsilon_nonterminals = set()
    for production in grammar.productions:
        if len(production.body) == 1 and isinstance(production.body[0], Terminal):
            terminal = production.body[0].value
            if terminal not in symbol_dict:
                symbol_dict[terminal] = set()
            symbol_dict[terminal].add(production.head)
        elif len(production.body) == 1 and isinstance(production.body[0], Epsilon):
            epsilon_nonterminals.add(production.head)

    return symbol_dict, epsilon_nonterminals


def get_boolean_decomposition(grammar: CFG, graph: nx.MultiDiGraph):
    boolean_decomposition = {
        nonterminal: lil_array((len(graph.nodes), len(graph.nodes)), dtype=bool)
        for nonterminal in grammar.variables
    }

    symbol_dict, epsilon_nonterminals = get_grammar_helping_info(grammar)

    for edge in graph.edges(data=True):
        first, second, edge_data = edge
        if edge_data["label"] in symbol_dict:
            for terminal in symbol_dict[edge_data["label"]]:
                boolean_decomposition[terminal][int(first), int(second)] = True

    for epsilon_nonterminal in epsilon_nonterminals:
        for i in range(len(graph.nodes)):
            boolean_decomposition[epsilon_nonterminal][i, i] = True

    return boolean_decomposition


def check_matrices_changing(prev_boolean_decomposition, curr_boolean_decomposition):
    if prev_boolean_decomposition is None:
        return True

    for nonterminal in prev_boolean_decomposition.keys():
        if (
            prev_boolean_decomposition[nonterminal].nnz
            != curr_boolean_decomposition[nonterminal].nnz
        ):
            return True

    return False


def copy_decomposition(boolean_decomposition):
    copied_decomposition = dict()
    for nonterminal in boolean_decomposition.keys():
        copied_decomposition[nonterminal] = boolean_decomposition[nonterminal].copy()

    return copied_decomposition


def matrix_algo(grammar: CFG, graph: nx.MultiDiGraph, start=None, end=None):
    if not is_in_wcnf(grammar):
        grammar = convert_cfg_to_wcnf(grammar)

    boolean_decomposition = get_boolean_decomposition(grammar, graph)
    not_start_productions = []
    for production in grammar.productions:
        if len(production.body) == 2:
            not_start_productions.append(production)

    current = boolean_decomposition.copy()
    if len(not_start_productions) > 0:
        previous = None
        while check_matrices_changing(previous, current):
            previous = copy_decomposition(current)
            for production in not_start_productions:
                current[production.head] += (
                    current[production.body[0]] @ current[production.body[1]]
                )
    result_set = {
        (nonterminal, v, w)
        for nonterminal in grammar.variables
        for v, w in zip(*current[nonterminal].nonzero())
    }

    if end is not None or start is not None:
        filtered_result_set = set()
        for (nonterminal, first, second) in result_set:
            if first in start:
                filtered_result_set.add((nonterminal, first, second))

        if end is None:
            return filtered_result_set

        new_filtered_set = set()
        for (nonterminal, first, second) in filtered_result_set:
            if second in end:
                new_filtered_set.add((nonterminal, first, second))

        return new_filtered_set

    return result_set
