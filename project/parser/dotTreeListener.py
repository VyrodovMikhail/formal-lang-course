from antlr4.tree.Tree import TerminalNode
from antlr4 import ParserRuleContext
from pydot import Dot, Node, Edge

from project.parser.languageListener import languageListener


class DotTreeListener(languageListener):
    def __init__(self, tree: Dot, rules):
        self.tree = tree
        self.num_nodes = 0
        self.nodes_stack = []
        self.rules = rules

    def enterEveryRule(self, ctx: ParserRuleContext):
        self.tree.add_node(Node(self.num_nodes, label=self.rules[ctx.getRuleIndex()]))

        if self.num_nodes:
            self.tree.add_edge(Edge(self.nodes_stack[-1], self.num_nodes))

        self.nodes_stack.append(self.num_nodes)
        self.num_nodes += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.nodes_stack.pop()

    def visitTerminal(self, node: TerminalNode):
        self.tree.add_node(Node(self.num_nodes, label=f"{node}"))
        self.tree.add_edge(Edge(self.nodes_stack[-1], self.num_nodes))
        self.num_nodes += 1
