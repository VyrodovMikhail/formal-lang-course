from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from pydot import Dot

from project.parser.languageLexer import languageLexer
from project.parser.languageParser import languageParser
from project.parser.dotTreeListener import DotTreeListener


def parse(prog_str: str) -> languageParser:
    stream = InputStream(prog_str)
    lexer = languageLexer(stream)
    tokens = CommonTokenStream(lexer)
    return languageParser(tokens)


def check_program_correctness(prog_str: str):
    lang_parser = parse(prog_str)
    lang_parser.prog()

    return lang_parser.getNumberOfSyntaxErrors() == 0


def parse_to_dot(prog_str: str, path_to_dot):
    if not check_program_correctness(prog_str):
        raise Exception("There are syntax errors in program")

    ast = parse(prog_str).prog()
    dot_file = Dot("ast", graph_type="digraph")
    listener = DotTreeListener(dot_file, languageParser.ruleNames)

    walker = ParseTreeWalker()
    walker.walk(listener, ast)

    dot_file.write(path_to_dot)
