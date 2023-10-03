import networkx as nx

from scipy.sparse import lil_array, lil_matrix

from project.automata_utils import build_nfa_from_graph, build_minimal_dfa_from_regex
from project.automata_intersection import intersect_automata


def get_transitive_closure(intersection_matricies: dict[lil_matrix]) -> lil_matrix:
    states_count, _ = next(iter(intersection_matricies.values())).shape
    reach_matrix = lil_array((states_count, states_count), dtype=bool)

    reach_matrix = sum(intersection_matricies.values(), start=reach_matrix)

    prev_nonzero_count = -1
    curr_nonzero_count = reach_matrix.count_nonzero()
    while prev_nonzero_count != curr_nonzero_count:
        reach_matrix += reach_matrix @ reach_matrix
        prev_nonzero_count = curr_nonzero_count
        curr_nonzero_count = reach_matrix.count_nonzero()

    return reach_matrix


def rpq(
    graph: nx.MultiDiGraph,
    regex_str: str,
    start_vertices: set = None,
    final_vertices: set = None,
):
    nfa_from_graph = build_nfa_from_graph(graph, start_vertices, final_vertices)
    dfa_from_regex = build_minimal_dfa_from_regex(regex_str)
    (intersection_matrices, start_states, final_states) = intersect_automata(
        nfa_from_graph, dfa_from_regex
    )

    transitive_closure = get_transitive_closure(intersection_matrices)

    result_paths = set()
    regex_dfa_states_number = len(list(dfa_from_regex.states))
    graph_nfa_states = list(nfa_from_graph.states)
    edges_indices = transitive_closure.nonzero()
    rows_indexes, columns_indexes = edges_indices

    for first, second in zip(rows_indexes, columns_indexes):
        if first in start_states and second in final_states:
            result_paths.add(
                (
                    graph_nfa_states[first // regex_dfa_states_number],
                    graph_nfa_states[second // regex_dfa_states_number],
                )
            )

    return result_paths
