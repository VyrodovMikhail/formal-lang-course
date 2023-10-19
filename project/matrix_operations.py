from scipy.sparse import lil_matrix, block_diag, lil_array


def construct_direct_sums_matrices(
    regex_decomposition: dict[lil_matrix], graph_decomposition: dict[lil_matrix]
):
    labels_intersection = set(regex_decomposition.keys()).intersection(
        set(graph_decomposition.keys())
    )

    direct_sums = dict()
    for label in labels_intersection:
        direct_sums[label] = block_diag(
            (regex_decomposition[label], graph_decomposition[label]), format="csr"
        )

    return direct_sums


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
