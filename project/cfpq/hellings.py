from typing import Union
from pathlib import Path

import networkx as nx
from pyformlang.cfg import CFG, Terminal, Variable, Epsilon

from project.context_free_grammars.cfg_operations import (
    convert_cfg_to_wcnf,
    is_in_wcnf,
    read_grammar_from_file,
)
from project.graph_utils import read_from_dot


def get_start_set(grammar: CFG, graph: nx.MultiDiGraph):
    start_set = set()
    graph_nodes = list(graph.nodes)
    for production in grammar.productions:

        if production.body == [Epsilon()]:
            for node in graph_nodes:
                start_set.add((production.head, node, node))
        elif len(production.body) == 1 and type(production.body[0]) is Terminal:
            symbol = production.body[0].value
            for edge in graph.edges(data=True):
                first, second, edge_data = edge
                if symbol == edge_data["label"]:
                    start_set.add((production.head, first, second))
    return start_set


def construct_production_dict(grammar: CFG):
    production_dict = dict()
    for production in grammar.productions:
        if len(production.body) == 2:
            production_key = production.body[0].value + production.body[1].value
            if production_key not in production_dict:
                production_dict[production_key] = [production.head]
            else:
                production_dict[production_key].append(production.head)

    return production_dict


def start_hellings(
    grammar: Union[Path, CFG],
    start_symbol: str,
    graph: Union[str, nx.MultiDiGraph],
    start=None,
    end=None,
    nonterminal=None,
):
    if isinstance(grammar, Path):
        grammar = read_grammar_from_file(grammar, start_symbol)

    if isinstance(graph, str):
        graph = read_from_dot(graph)

    return hellings(grammar, graph, start, end, nonterminal)


def hellings(
    grammar: CFG, graph: nx.MultiDiGraph, start=None, end=None, nonterminal=None
):
    if not is_in_wcnf(grammar):
        grammar = convert_cfg_to_wcnf(grammar)

    production_dict = construct_production_dict(grammar)
    processing_set = get_start_set(grammar, graph)
    result_set = processing_set.copy()
    while len(processing_set):
        nonterminal_p, first_p, second_p = processing_set.pop()

        result_set_copy = result_set.copy()
        for (nonterminal_r, first_r, second_r) in result_set_copy:
            if second_r != first_p:
                continue
            production_key = nonterminal_r.value + nonterminal_p.value

            if production_key in production_dict:
                for nonterminal_k in production_dict[production_key]:
                    new_path = (nonterminal_k, first_r, second_p)
                    if new_path not in result_set:
                        processing_set.add(new_path)
                        result_set.add(new_path)

        result_set_copy = result_set.copy()
        for (nonterminal_r, first_r, second_r) in result_set_copy:
            if first_r != second_p:
                continue
            production_key = nonterminal_p.value + nonterminal_r.value

            if production_key in production_dict:
                for nonterminal_k in production_dict[production_key]:
                    new_path = (nonterminal_k, first_p, second_r)
                    if new_path not in result_set:
                        processing_set.add(new_path)
                        result_set.add(new_path)

    if end is not None or start is not None or nonterminal is not None:
        filtered_result_set = set()
        for (nonterminall, first, second) in result_set:
            if first in start:
                filtered_result_set.add((nonterminall, first, second))

        if end is None and nonterminal is None:
            return filtered_result_set

        new_filtered_set = set()
        for (nonterminall, first, second) in filtered_result_set:
            if second in end:
                new_filtered_set.add((nonterminall, first, second))

        if nonterminal is None:
            return new_filtered_set

        final_filtered_set = set()
        for (nonterminall, first, second) in new_filtered_set:
            if nonterminall == nonterminal:
                final_filtered_set.add((nonterminall, first, second))

        return final_filtered_set

    return result_set
