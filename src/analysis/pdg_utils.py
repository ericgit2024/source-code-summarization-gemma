import networkx as nx

class PDGBuilder:
    def __init__(self, ast_analyzer, cfg):
        self.ast_analyzer = ast_analyzer
        self.cfg = cfg

    def build_pdg(self, node):
        # Program Dependence Graph = Control Dependence + Data Dependence
        pdg = nx.DiGraph()
        
        # Copy nodes from CFG
        pdg.add_nodes_from(self.cfg.nodes(data=True))
        
        # 1. Control Dependence (simplified: parent-child in AST often implies control dep in structured code)
        # We can reuse the CFG edges that represent nesting/branching
        for u, v, data in self.cfg.edges(data=True):
            pdg.add_edge(u, v, type='control')
            
        # 2. Data Dependence
        # We need to find where variables are defined and used.
        # This requires a data flow analysis.
        # For this prototype, we will link usages of the same variable name.
        # This is "Name Dependence" which is a weak form of Data Dependence but useful for LLMs.
        
        var_usages = {} # var_name -> list of node_ids
        
        for node_id, data in pdg.nodes(data=True):
            code = data.get('code', '')
            # Heuristic: if code is a variable name
            if data.get('label') == 'identifier':
                var_name = code
                if var_name not in var_usages:
                    var_usages[var_name] = []
                var_usages[var_name].append(node_id)
                
        # Link usages
        for var_name, nodes in var_usages.items():
            for i in range(len(nodes) - 1):
                # Link sequential usages
                pdg.add_edge(nodes[i], nodes[i+1], type='data', variable=var_name)
                
        return pdg

    def get_pdg_summary(self, pdg):
        data_edges = [e for u,v,e in pdg.edges(data=True) if e.get('type') == 'data']
        return {
            "data_dependencies": len(data_edges)
        }
