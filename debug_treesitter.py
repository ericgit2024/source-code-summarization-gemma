import tree_sitter_python
from tree_sitter import Language, Parser

try:
    lang = Language(tree_sitter_python.language())
    parser = Parser(lang)
    tree = parser.parse(b"def foo(): pass")
    query = lang.query("(function_definition) @func")
    print("Query methods:", dir(query))
except Exception as e:
    print(f"Error: {e}")
