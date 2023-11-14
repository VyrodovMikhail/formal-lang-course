from typing import Tuple

import cfpq_data
import networkx as nx


def get_graph_from_name(name: str) -> nx.MultiDiGraph:
    graph_path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(graph_path)


def get_graph_properties(graph: nx.MultiDiGraph) -> Tuple[int, int, dict]:
    nodes_number = graph.number_of_nodes()
    edges_number = graph.size()
    edges_marks = dict()
    for edge in graph.edges(data=True):
        first, second, edge_data = edge
        for mark in edge_data.keys():
            if mark not in edges_marks:
                edges_marks[mark] = set()
            if edge_data[mark] not in edges_marks[mark]:
                edges_marks[mark].add(edge_data[mark])
    return nodes_number, edges_number, edges_marks


def create_labeled_two_cycles_graph(
    first_nodes_count: int,
    second_nodes_count: int,
    edge_labels: Tuple[str, str],
    name: str,
):
    new_graph = cfpq_data.labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, common_node=0, labels=edge_labels
    )
    nx.nx_pydot.write_dot(new_graph, name)
    print(f"Two cycles graph was written to {name} file.")
    return new_graph


def read_from_dot(path: str):
    graph = nx.drawing.nx_pydot.read_dot(path)
    if "\\n" in graph:
        graph.remove_node("\\n")

    return graph
