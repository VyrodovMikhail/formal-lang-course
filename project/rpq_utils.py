import networkx as nx

from project.automata_utils import build_nfa_from_graph, build_minimal_dfa_from_regex
from project.automata_intersection import intersect_automata


def rpq(
    graph: nx.MultiDiGraph,
    regex_str: str,
    start_vertices: set = None,
    final_vertices: set = None,
):
    nfa_from_graph = build_nfa_from_graph(graph, start_vertices, final_vertices)
    dfa_from_regex = build_minimal_dfa_from_regex(regex_str)
    intersection = intersect_automata(nfa_from_graph, dfa_from_regex)
    intersection_graph = intersection.to_networkx()
    transitive_closure = nx.transitive_closure(intersection_graph, reflexive=True)

    result_paths = set()
    start_states = intersection.start_states
    final_states = intersection.final_states
    regex_dfa_states_number = len(list(dfa_from_regex.states))
    graph_nfa_states = list(nfa_from_graph.states)

    for (first, second) in transitive_closure.edges():
        if first in start_states and second in final_states:
            result_paths.add(
                (
                    graph_nfa_states[first // regex_dfa_states_number],
                    graph_nfa_states[second // regex_dfa_states_number],
                )
            )

    return result_paths
