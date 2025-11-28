import sys
from antlr4 import *
from AlgoritmiaLexer import AlgoritmiaLexer
from AlgoritmiaParser import AlgoritmiaParser
from VisitorAlgoritmia import Visitor

if len(sys.argv) > 1:
    input_stream = FileStream(sys.argv[1],encoding = 'utf-8')
    lexer = AlgoritmiaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = AlgoritmiaParser(token_stream)
    tree = parser.root()

    if len(sys.argv) > 2:
        visitor = Visitor(sys.argv[2])
    else:
        visitor = Visitor()
    
    visitor.visit(tree)
else:
    print("Usage: python test.py <inputfile>")