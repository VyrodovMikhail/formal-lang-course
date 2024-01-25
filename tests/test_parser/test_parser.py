from pathlib import Path

from project.parser.parser import check_program_correctness, parse_to_dot

correct_cases = [
    "x = 5",
    "x = {1, 2, 3}",
    'x = {"1", "a"}',
    'x = r"a* b"',
    "x = false",
    'graph = load_from_file("file_path")',
    "my_set = get_vertices(graph)",
    "my_set = set_start({1}, graph)",
    'my_set = add_start("new_start", graph)',
    'filtered_vertices = filter((fun x -> x in {"A", "B"}), get_start(vertices))',
    "new_graph = graph_1 intersect graph_2",
    "intersection = first_cond && second_cond",
    "not_cond = not cond",
]

incorrect_cases = [
    "1 = 5",
    "444x = 5",
    "x = {1, 2 3}",
    "x = {1, 2, 3",
    "my_set = set_start(1, graph)",
    "my_set = set_start(1, graph",
    'my_set = adddd_start("new_start", graph)',
    "intersection = first_cond &&",
    'filtered_vertices = filter((fun x -> x in , "B"}), get_start(vertices))',
    'filtered_vertices = filter((fun x -> x in {"A", "B"}), get_startt(vertices))',
]

test_case = """
my_graph = load_from_file("./filename")
vertices = get_vertices(my_graph)
filtered_vertices = filter((fun x -> x in {"A", "B"}), vertices)
print filtered_vertices
"""


def test_parser():
    for case in correct_cases:
        assert check_program_correctness(case)

    for case in incorrect_cases:
        assert not check_program_correctness(case)


def test_parse_to_dot():
    expected = Path("./tests/test_parser/expected.dot")
    generated = Path("./tests/test_parser/generated.dot")

    parse_to_dot(test_case, generated)

    with open(generated, "r") as generated_text:
        with open(expected, "r") as expected_text:
            assert generated_text.read() == expected_text.read()
