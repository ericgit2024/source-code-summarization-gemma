import tree_sitter_python
from tree_sitter import Language, Parser

try:
    lang = Language(tree_sitter_python.language())
    parser = Parser(lang)
    tree = parser.parse(b"def foo(): pass")
    query = lang.query("(function_definition) @func")
    
    import tree_sitter
    print("Dir of tree_sitter:", dir(tree_sitter))
    if hasattr(tree_sitter, 'QueryCursor'):
        print("QueryCursor exists!")
        cursor = tree_sitter.QueryCursor()
        print("Dir of QueryCursor:")
        for d in dir(cursor):
            print(d)
            
        if hasattr(cursor, 'matches'):
            print("Cursor has matches!")
            try:
                matches = cursor.matches(query, tree.root_node)
                print("Cursor matches result:", list(matches))
            except Exception as e:
                print(f"Cursor matches error: {e}")
    else:
        print("QueryCursor does not exist.")
    
    if hasattr(query, 'matches'):
        print("Has matches method")
        try:
            matches = query.matches(tree.root_node)
            print("Matches result:", list(matches))
        except Exception as e:
            print("Matches call failed:", e)
            
    if hasattr(query, 'captures'):
        print("Has captures method")
    else:
        print("No captures method")
        
except Exception as e:
    print(f"Error: {e}")
