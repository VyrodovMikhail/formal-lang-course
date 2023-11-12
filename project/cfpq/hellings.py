import networkx as nx


from pyformlang.cfg import CFG, Terminal, Variable, Epsilon
from project.context_free_grammars.cfg_operations import convert_cfg_to_wcnf, is_in_wcnf


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


"""def construct_vertices_dicts(start_set):
    first_v_dict = dict()
    second_v_dict = dict()
    for (nonterminal, first, second) in start_set:
        if first not in first_v_dict:
            first_v_dict[first] = [nonterminal, second]
        else:
            first_v_dict[first].append([nonterminal, second])

        if second not in second_v_dict:
            second_v_dict[second] = [nonterminal, first]
        else:
            second_v_dict[second].append([nonterminal, first])

    return first_v_dict, second_v_dict """


def hellings(grammar: CFG, graph: nx.MultiDiGraph):
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

    return result_set
