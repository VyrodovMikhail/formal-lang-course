import networkx as nx

from pyformlang.finite_automaton import FiniteAutomaton
from scipy.sparse import lil_matrix, vstack

from project.matrix_operations import construct_direct_sums_matrices
from project.automata_operations.automaton_construction import (
    build_nfa_from_graph,
    build_minimal_dfa_from_regex,
)
from project.automata_operations.automaton_boolean_decomposition import (
    make_state_indices_dict,
    get_boolean_decomposition,
)
from project.rpq.bfs_rpq_mode import BfsRpqMode


def create_front_matrix(
    regex: FiniteAutomaton, graph: FiniteAutomaton, graph_start_states_indices: set
) -> lil_matrix:
    regex_states_count, graph_states_count = len(regex.states), len(graph.states)
    front = lil_matrix(
        (regex_states_count, regex_states_count + graph_states_count), dtype=bool
    )
    graph_front_part = lil_matrix((1, graph_states_count))
    regex_states_dict = make_state_indices_dict(regex.states)
    regex_start_states_indices = [
        regex_states_dict[state] for state in regex.start_states
    ]

    for state_index in graph_start_states_indices:
        graph_front_part[0, state_index] = True
    for i in range(regex_states_count):
        front[i, i] = True
        if i in regex_start_states_indices:
            front[i, regex_states_count:] = graph_front_part

    return front


def transform_front(left_matrix_dim: int, front: lil_matrix) -> lil_matrix:
    transformed_front = lil_matrix(front.shape, dtype=bool)
    left_submatrix = front[:, 0:left_matrix_dim]
    for row, column in zip(*left_submatrix.nonzero()):
        extracted_row = front[row]
        if extracted_row.count_nonzero() > 1:
            transformed_front[
                (row // left_matrix_dim) * left_matrix_dim + column
            ] += extracted_row

    return transformed_front


def extract_answer_from_front(
    regex: FiniteAutomaton,
    regex_states_dict,
    graph_automaton: FiniteAutomaton,
    graph_states_dict,
    front_matrix: lil_matrix,
    rpq_for_every_vertex: BfsRpqMode,
):
    regex_states_count = len(regex.states)
    regex_final_state_indices = [
        regex_states_dict[state] for state in regex.final_states
    ]
    graph_final_state_indices = [
        graph_states_dict[state] for state in graph_automaton.final_states
    ]
    graph_start_state_indices = [
        graph_states_dict[state] for state in graph_automaton.start_states
    ]
    result = set()
    for row, column in zip(*front_matrix.nonzero()):
        if (
            regex_states_count <= column
            and row % regex_states_count in regex_final_state_indices
            and column - regex_states_count in graph_final_state_indices
        ):
            vertex_index = column - regex_states_count
            if rpq_for_every_vertex == BfsRpqMode.RPQ_FOR_EVERY_VERTEX:
                start_index = graph_start_state_indices[row // len(regex.states)]
                result.add((start_index, vertex_index))
            else:
                result.add(vertex_index)

    return result


def bfs_rpq_automata(
    regex: FiniteAutomaton,
    graph_automaton: FiniteAutomaton,
    rpq_for_every_vertex: BfsRpqMode,
):
    regex_states_dict = make_state_indices_dict(regex.states)
    graph_states_dict = make_state_indices_dict(graph_automaton.states)
    graph_start_states_indices = [
        graph_states_dict[state] for state in graph_automaton.start_states
    ]

    if rpq_for_every_vertex == BfsRpqMode.RPQ_FOR_EVERY_VERTEX:
        fronts = [
            create_front_matrix(regex, graph_automaton, {start_state})
            for start_state in graph_start_states_indices
        ]
        initial_front = vstack(fronts)
    else:
        initial_front = create_front_matrix(
            regex, graph_automaton, set(graph_start_states_indices)
        )

    first_boolean_decomposition = get_boolean_decomposition(regex)
    second_boolean_decomposition = get_boolean_decomposition(graph_automaton)
    direct_sums = construct_direct_sums_matrices(
        first_boolean_decomposition, second_boolean_decomposition
    )

    visited = lil_matrix(initial_front.shape, dtype=bool)
    prev_front = None
    first_iteration_flag = True

    while prev_front is None or visited.count_nonzero() != prev_front.count_nonzero():
        prev_front = visited.copy()
        for label in direct_sums.keys():
            if first_iteration_flag:
                front = initial_front @ direct_sums[label]
            else:
                front = visited @ direct_sums[label]
            visited += transform_front(len(regex.states), front)

        first_iteration_flag = False

    return extract_answer_from_front(
        regex,
        regex_states_dict,
        graph_automaton,
        graph_states_dict,
        visited,
        rpq_for_every_vertex,
    )


def bfs_rpq(
    graph: nx.MultiDiGraph,
    regex_str: str,
    start_vertices: set = None,
    final_vertices: set = None,
    rpq_mode: BfsRpqMode = BfsRpqMode.RPQ_FOR_VERTICES_SET,
):
    nfa_from_graph = build_nfa_from_graph(graph, start_vertices, final_vertices)
    dfa_from_regex = build_minimal_dfa_from_regex(regex_str)

    return bfs_rpq_automata(dfa_from_regex, nfa_from_graph, rpq_mode)
