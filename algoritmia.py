#!/usr/bin/env python3
# algoritmia.py

import sys
from antlr4 import *
from AlgoritmiaLexer import AlgoritmiaLexer
from AlgoritmiaParser import AlgoritmiaParser
from AlgVisitor import Visitor, AlgoritmiaException


def main():
    # Verifica argumentos
    if len(sys.argv) < 2:
        print("Uso: python3 algoritmia.py <archivo.alg>")
        print("Ejemplo: python3 algoritmia.py tests/test1.alg")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Lee el archivo
        input_stream = FileStream(input_file, encoding='utf-8')

        # Lexer: texto → tokens
        lexer = AlgoritmiaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)

        # Parser: tokens → árbol
        parser = AlgoritmiaParser(token_stream)
        tree = parser.root()

        # Verifica errores de sintaxis
        if parser.getNumberOfSyntaxErrors() > 0:
            print(f"Error de sintaxis en {input_file}")
            sys.exit(1)

        # Visitor: interpreta el árbol
        visitor = Visitor()
        visitor.visit(tree)

    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{input_file}'")
        sys.exit(1)

    except AlgoritmiaException as e:
        print(e.message)
        sys.exit(1)

    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()