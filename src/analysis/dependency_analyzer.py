import os
import tree_sitter

class DependencyAnalyzer:
    def __init__(self, ast_analyzer):
        self.ast_analyzer = ast_analyzer
        self.language_name = ast_analyzer.language_name

    def analyze(self, repo_root, file_path, function_node):
        """
        Analyzes the dependencies of a function node.
        Returns a dictionary representing the graph:
        {
            "nodes": [{"id": "name", "type": "function"|"file", "label": "..."}],
            "edges": [{"source": "id1", "target": "id2", "relation": "calls"|"imports"}]
        }
        """
        nodes = []
        edges = []
        
        # 1. Add the function itself as the central node
        func_name = self._get_node_name(function_node)
        if not func_name:
            func_name = "unknown_function"
            
        root_id = f"func:{func_name}"
        nodes.append({"id": root_id, "type": "function", "label": func_name, "style": "filled", "fillcolor": "lightblue"})

        # 2. Analyze Imports in the current file
        # We need to parse the whole file to get imports, but we might already have the tree?
        # The function_node is part of a tree. We can go up to the root.
        root_node = function_node
        while root_node.parent:
            root_node = root_node.parent
            
        imports = self._extract_imports(root_node)
        
        # 3. Analyze Calls within the function
        calls, _ = self.ast_analyzer.extract_dependencies(function_node)
        
        # 4. Resolve Dependencies
        # For each call, check if it matches an import or is a local function
        for call in calls:
            # Simple heuristic: if call matches an import alias, link to that file/module
            # If not, assume it's a local function or built-in (we'll mark as local for now)
            
            matched_import = None
            for imp in imports:
                if imp['alias'] == call or imp['name'].endswith(f".{call}") or imp['name'] == call:
                    matched_import = imp
                    break
            
            if matched_import:
                target_id = f"mod:{matched_import['name']}"
                # Add module node if not exists
                if not any(n['id'] == target_id for n in nodes):
                    nodes.append({"id": target_id, "type": "module", "label": matched_import['name'], "shape": "box"})
                
                edges.append({"source": root_id, "target": target_id, "relation": "calls_external"})
            else:
                # Assume local call
                target_id = f"func:{call}"
                if not any(n['id'] == target_id for n in nodes):
                    nodes.append({"id": target_id, "type": "function", "label": call})
                edges.append({"source": root_id, "target": target_id, "relation": "calls"})

        return {"nodes": nodes, "edges": edges}

    def _get_node_name(self, node):
        # Helper to extract name from function definition node
        # This duplicates some logic from ASTAnalyzer but is needed here
        if self.language_name == 'python':
            child = node.child_by_field_name('name')
            return child.text.decode('utf8') if child else None
        return None

    def _extract_imports(self, root_node):
        imports = []
        if self.language_name == 'python':
            # Query for imports
            query_scm = """
            (import_statement
                name: (dotted_name) @name
            ) @import
            (import_from_statement
                module_name: (dotted_name) @module
                name: (dotted_name) @name
            ) @import_from
            (aliased_import
                name: (dotted_name) @name
                alias: (identifier) @alias
            ) @aliased
            """
            # Note: This is a simplified query and might need adjustment based on exact tree-sitter grammar
            # For now, let's do a manual traversal for robustness or use a simpler query
            
            # Manual traversal for robustness
            cursor = root_node.walk()
            
            visited_children = False
            while True:
                if not visited_children:
                    if cursor.node.type == 'import_statement':
                        # import x, y
                        for child in cursor.node.children:
                            if child.type == 'dotted_name':
                                name = child.text.decode('utf8')
                                imports.append({'name': name, 'alias': name})
                    elif cursor.node.type == 'import_from_statement':
                        # from x import y
                        module_name = None
                        for child in cursor.node.children:
                            if child.type == 'dotted_name' and not module_name: # first one is module
                                module_name = child.text.decode('utf8')
                            elif child.type == 'dotted_name': # imported name
                                name = child.text.decode('utf8')
                                full_name = f"{module_name}.{name}"
                                imports.append({'name': full_name, 'alias': name})
                            elif child.type == 'aliased_import':
                                # from x import y as z
                                # This needs deeper parsing, skipping for MVP simplicity
                                pass

                if cursor.goto_first_child():
                    visited_children = False
                elif cursor.goto_next_sibling():
                    visited_children = False
                elif cursor.goto_parent():
                    visited_children = True
                else:
                    break
                    
        return imports
