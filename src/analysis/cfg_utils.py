import networkx as nx

class CFGBuilder:
    def __init__(self, ast_analyzer):
        self.ast_analyzer = ast_analyzer

    def build_cfg(self, node):
        # Simplified CFG construction
        # Nodes are AST nodes (or IDs), Edges represent control flow
        cfg = nx.DiGraph()
        
        # We will traverse the AST and add edges for control flow structures
        # This is a high-level approximation for summarization context
        
        def traverse(n, parent_id=None):
            node_id = f"{n.start_point[0]}:{n.start_point[1]}"
            label = n.type
            cfg.add_node(node_id, label=label, code=n.text.decode('utf8'))
            
            if parent_id:
                cfg.add_edge(parent_id, node_id)
            
            # Handle control flow specifically
            # If 'if_statement', children are branches.
            # If 'for_statement', loop back edge.
            
            # For now, we just link children to parent to show structure, 
            # and add specific flow edges for known constructs.
            
            last_child_id = None
            for child in n.children:
                child_id = traverse(child, node_id)
                
                # Sequential flow between statements in a block
                if n.type in ['block', 'module'] and last_child_id:
                     # This is a bit loose, but captures sequence
                     cfg.add_edge(last_child_id, child_id, type='sequence')
                
                last_child_id = child_id
                
            return node_id

        traverse(node)
        return cfg

    def get_cfg_summary(self, cfg):
        # Return some stats about the CFG
        return {
            "nodes": cfg.number_of_nodes(),
            "edges": cfg.number_of_edges(),
            "cyclomatic_complexity": self.calculate_cyclomatic(cfg)
        }

    def calculate_cyclomatic(self, cfg):
        # E - N + 2P (P=1 for single function)
        return cfg.number_of_edges() - cfg.number_of_nodes() + 2
