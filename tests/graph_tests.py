import cfpq_data
import networkx as nx

from project import graph_utils


def test_get_graph_properties():
    bzip_path = cfpq_data.download("bzip")
    bzip = cfpq_data.graph_from_csv(bzip_path)
    expected_nodes_number = bzip.number_of_nodes()
    expected_edges_number = bzip.size()
    expected_edges_marks = {"label": {"a", "d"}}
    nodes_number, edges_number, edges_marks = graph_utils.get_graph_properties(bzip)
    assert expected_nodes_number == nodes_number
    assert expected_edges_number == edges_number
    assert expected_edges_marks == edges_marks


def assert_edges_are_equal(real_graph, graph_from_file):
    for edge in real_graph.edges(data=True):
        first, second, edge_data = edge
        assert graph_from_file.has_edge(str(first), str(second))
        real_edge_data = graph_from_file.get_edge_data(str(first), str(second))["0"]
        if real_edge_data is None:
            assert 0
        for mark in edge_data.keys():
            assert real_edge_data[mark] == edge_data[mark]


def test_create_labeled_two_cycles_graph():
    first_nodes_count = 5
    second_nodes_count = 10
    edge_labels = ("a", "b")
    name = "labeled_graph.dot"
    two_cycles_graph = cfpq_data.labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, common_node=0, labels=edge_labels
    )
    graph_utils.create_labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, edge_labels, name
    )

    real_graph = nx.nx_pydot.read_dot("labeled_graph.dot")

    # Removing last node because while reading from pydot we get additional '\n' node.
    if real_graph.has_node("\\n"):
        real_graph.remove_node("\\n")
    (
        expected_nodes_number,
        expected_edges_number,
        expected_edges_marks,
    ) = graph_utils.get_graph_properties(two_cycles_graph)
    nodes_number, edges_number, edges_marks = graph_utils.get_graph_properties(
        real_graph
    )

    assert expected_nodes_number == nodes_number
    assert expected_edges_number == edges_number
    assert expected_edges_marks == edges_marks

    assert_edges_are_equal(two_cycles_graph, real_graph)
