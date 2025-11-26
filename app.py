import streamlit as st
import tempfile
import os
from antlr4 import *
from AlgoritmiaLexer import AlgoritmiaLexer
from AlgoritmiaParser import AlgoritmiaParser
from AlgVisitor import Visitor, AlgoritmiaException

st.title("Intérprete Musical Algoritmia")

# Subir archivo
uploaded_file = st.file_uploader("Sube tu archivo .alg o .txt", type=['alg', 'txt'])

if uploaded_file is not None:
    # Mostrar el código cargado
    code = uploaded_file.read().decode('utf-8')
    st.code(code, language='text')

    # Botón ejecutar
    if st.button("Ejecutar"):
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.alg', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            # Ejecutar el intérprete
            input_stream = FileStream(tmp_path, encoding='utf-8')
            lexer = AlgoritmiaLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = AlgoritmiaParser(token_stream)
            tree = parser.root()

            if parser.getNumberOfSyntaxErrors() > 0:
                st.error("Error de sintaxis")
            else:
                visitor = Visitor()
                visitor.visit(tree)

                st.success("Ejecución completada")

                # Si se generó el MP3, ofrecer descarga
                if os.path.exists('music.mp3'):
                    with open('music.mp3', 'rb') as f:
                        st.download_button(
                            label="Descargar music.mp3",
                            data=f,
                            file_name="music.mp3",
                            mime="audio/mp3"
                        )

                    # Reproducir en la app
                    st.audio('music.mp3')
                else:
                    st.info("No se generó música")

        except AlgoritmiaException as e:
            st.error(f" {e.message}")
        except Exception as e:
            st.error(f" Error: {e}")
        finally:
            os.remove(tmp_path)