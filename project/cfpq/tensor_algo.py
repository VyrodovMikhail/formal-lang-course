from typing import Union
from pathlib import Path

import networkx as nx
from pyformlang.cfg import CFG, Variable
from scipy.sparse import lil_matrix, eye

from project.context_free_grammars.cfg_operations import (
    read_grammar_from_file,
)
from project.graph_utils import read_from_dot
from project.context_free_grammars.extended_context_free_grammar import ECFG
from project.automata_operations.recursive_finite_automaton import RFA
from project.automata_operations.automaton_construction import build_nfa_from_graph
from project.automata_operations.automaton_boolean_decomposition import (
    get_boolean_decomposition,
)
from project.matrix_operations import get_transitive_closure
from project.automata_operations.automata_intersection import (
    intersect_boolean_decompositions,
)


def start_tensor_algo(
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

    return tensor_algo(grammar, graph, start, end)


def tensor_algo(cfg: CFG, graph: nx.MultiDiGraph, start=None, end=None):
    grammar = ECFG.ecfg_from_cfg_class(cfg)
    rfa = RFA.rfa_from_ecfg(grammar)
    rfa.minimize()
    rfa_boolean_decomposition = rfa.get_binary_decomposition()
    rfa_states, rfa_start_states, rfa_final_states = rfa.get_states()
    rfa_states_list = list(rfa_states)

    graph_nfa = build_nfa_from_graph(graph)
    nfa_boolean_decomposition = get_boolean_decomposition(graph_nfa)
    nfa_states_list = list(graph_nfa.states)
    nfa_states_count = len(graph_nfa.states)

    diagonal_matrix = eye(nfa_states_count, dtype=bool)
    for nonterminal in cfg.get_nullable_symbols():
        nfa_boolean_decomposition[nonterminal.value] += diagonal_matrix

    prev_nonzero_count = 0
    curr_nonzero_count = 1
    while prev_nonzero_count != curr_nonzero_count:
        intersection_matrices = intersect_boolean_decompositions(
            rfa_boolean_decomposition, nfa_boolean_decomposition
        )

        transitive_closure_elems = list(
            zip(*get_transitive_closure(intersection_matrices).nonzero())
        )

        prev_nonzero_count = curr_nonzero_count
        curr_nonzero_count = len(transitive_closure_elems)
        if curr_nonzero_count == prev_nonzero_count:
            break

        for i, j in transitive_closure_elems:
            start_state = rfa_states_list[i // nfa_states_count]
            final_state = rfa_states_list[j // nfa_states_count]
            if (
                start_state not in rfa_start_states
                or final_state not in rfa_final_states
            ):
                continue

            new_graph_elem = lil_matrix(
                (nfa_states_count, nfa_states_count), dtype=bool
            )
            new_graph_elem[i % nfa_states_count, j % nfa_states_count] = True
            if start_state.value[0] not in nfa_boolean_decomposition:
                nfa_boolean_decomposition[start_state.value[0]] = lil_matrix(
                    (nfa_states_count, nfa_states_count), dtype=bool
                )
            if final_state.value[0] not in nfa_boolean_decomposition:
                nfa_boolean_decomposition[final_state.value[0]] = lil_matrix(
                    (nfa_states_count, nfa_states_count), dtype=bool
                )

            nfa_boolean_decomposition[start_state.value[0]] += new_graph_elem
            nfa_boolean_decomposition[final_state.value[0]] += new_graph_elem

    result_set = set()
    for symbol in nfa_boolean_decomposition.keys():
        if isinstance(symbol, Variable):
            bool_matrix = nfa_boolean_decomposition[symbol]
            for i, j in zip(*bool_matrix.nonzero()):
                start_state = nfa_states_list[i].value
                end_state = nfa_states_list[j].value

                result_set.add((symbol, start_state, end_state))

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
