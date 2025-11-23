import tree_sitter
from tree_sitter import Language, Parser
import os

# Note: In a real environment, we might need to build these languages or use the python bindings directly.
# For this implementation, we assume the user has `tree-sitter-python`, `tree-sitter-java`, etc. installed
# and we can load them. However, the standard python bindings often require building a library file.
# To make this robust for the user without complex build steps, we will try to use `tree_sitter_languages` if available,
# or fall back to standard loading.
# For this specific code, we will assume standard usage pattern or use a helper to build.

# Since we can't easily build .so/.dll files in this environment without a compiler guaranteed,
# we will write the code to assume the languages are available or can be built.

class ASTAnalyzer:
    def __init__(self, language_name='python'):
        self.language_name = language_name

    # load language first
        self.language = self._load_language(language_name)

    # NEW API: Parser(language=...) or Parser(language)
        if self.language:
            try:
                self.parser = Parser(self.language)
            except TypeError:
                # Fallback for older versions or different signatures
                self.parser = Parser()
                self.parser.set_language(self.language)
        else:
            self.parser = None


    def _load_language(self, language_name):
        # Try tree_sitter_languages first (easiest path)
        try:
            from tree_sitter_languages import get_language
            return get_language(language_name)
        except ImportError:
            pass

        # This is a simplified loader. In production, this needs to handle paths to .so files
        # or use `tree_sitter_languages` package which comes with pre-built binaries.
        try:
            import tree_sitter_python
            import tree_sitter_java
            import tree_sitter_javascript
            
            if language_name == 'python':
                return Language(tree_sitter_python.language())
            elif language_name == 'java':
                return Language(tree_sitter_java.language())
            elif language_name == 'javascript':
                return Language(tree_sitter_javascript.language())
            else:
                raise ValueError(f"Unsupported language: {language_name}")
        except ImportError:
             # Fallback or placeholder if specific bindings aren't installed
             # This might fail if not properly set up.
             print(f"Warning: Could not load tree-sitter bindings for {language_name}. Ensure packages are installed.")
             return None
        except TypeError as e:
             print(f"Error loading language {language_name}: {e}. Check tree-sitter version compatibility.")
             return None

    def parse(self, code):
        if not self.language or not self.parser:
            return None
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree

    def get_function_node(self, tree, function_name):
        # Simple traversal to find a function definition with the given name
        root_node = tree.root_node
        
        # This query is language specific.
        if self.language_name == 'python':
            query_scm = f"""
            (function_definition
              name: (identifier) @name
              (#eq? @name "{function_name}")
            ) @function
            """
        elif self.language_name == 'java':
            query_scm = f"""
            (method_declaration
              name: (identifier) @name
              (#eq? @name "{function_name}")
            ) @method
            """
        elif self.language_name == 'javascript':
             query_scm = f"""
            (function_declaration
              name: (identifier) @name
              (#eq? @name "{function_name}")
            ) @function
            """
        else:
            return None

        query = self.language.query(query_scm)
        
        # Handle different tree-sitter versions for QueryCursor
        try:
            # New API: QueryCursor(query)
            cursor = tree_sitter.QueryCursor(query)
            matches = cursor.matches(root_node)
        except TypeError:
            # Old API: QueryCursor()
            cursor = tree_sitter.QueryCursor()
            matches = cursor.matches(query, root_node)
        
        for match in matches:
            # match can be (id, captures) or just match object depending on version
            # We assume standard (id, captures) tuple or object with captures
            if isinstance(match, tuple):
                captures = match[1]
            else:
                captures = match.captures # if object
            
            if 'function' in captures:
                return captures['function'][0]
            if 'method' in captures:
                return captures['method'][0]
        return None

    def extract_dependencies(self, node):
        # Extract calls and variables
        calls = []
        variables = []
        
        if self.language_name == 'python':
            call_query = self.language.query("(call function: (identifier) @func_name)")
            var_query = self.language.query("(identifier) @var_name")
            
            # Calls
            try:
                cursor = tree_sitter.QueryCursor(call_query)
                call_matches = cursor.matches(node)
            except TypeError:
                cursor = tree_sitter.QueryCursor()
                call_matches = cursor.matches(call_query, node)
            
            for match in call_matches:
                if isinstance(match, tuple):
                    captures = match[1]
                else:
                    captures = match.captures

                if 'func_name' in captures:
                    for n in captures['func_name']:
                        calls.append(n.text.decode('utf8'))
            
            # Variables
            try:
                cursor = tree_sitter.QueryCursor(var_query)
                var_matches = cursor.matches(node)
            except TypeError:
                cursor = tree_sitter.QueryCursor()
                var_matches = cursor.matches(var_query, node)

            for match in var_matches:
                if isinstance(match, tuple):
                    captures = match[1]
                else:
                    captures = match.captures

                if 'var_name' in captures:
                    for n in captures['var_name']:
                        variables.append(n.text.decode('utf8'))
                
        return list(set(calls)), list(set(variables))

    def get_complexity(self, node):
        # Cyclomatic complexity approximation: 1 + number of branching nodes
        complexity = 1
        branch_nodes = ['if_statement', 'for_statement', 'while_statement', 'case_clause', 'except_clause']
        
        def traverse(n):
            nonlocal complexity
            if n.type in branch_nodes:
                complexity += 1
            for child in n.children:
                traverse(child)
                
        traverse(node)
        return complexity
