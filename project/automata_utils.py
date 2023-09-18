from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
import networkx as nx


def build_minimal_dfa_from_regex(regex_str: str) -> DeterministicFiniteAutomaton:
    regex = Regex(regex_str)
    epsilon_nfa = regex.to_epsilon_nfa()
    minimal_dfa = epsilon_nfa.minimize()
    return minimal_dfa


def build_nfa_from_graph(
    graph: nx.MultiDiGraph, start_vertices: set = None, end_vertices: set = None
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    if start_vertices is None:
        start_vertices = graph.nodes
    if end_vertices is None:
        end_vertices = graph.nodes

    for start_vertice in start_vertices:
        if not graph.has_node(start_vertice):
            raise Exception("Wrong start states")
    for end_vertice in end_vertices:
        if not graph.has_node(end_vertice):
            raise Exception("Wrong final states")

    for start_state in start_vertices:
        nfa.add_start_state(start_state)
    for end_state in end_vertices:
        nfa.add_final_state(end_state)

    return nfa
