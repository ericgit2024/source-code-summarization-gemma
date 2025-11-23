from .ast_utils import ASTAnalyzer
from .cfg_utils import CFGBuilder
from .pdg_utils import PDGBuilder
from .dependency_analyzer import DependencyAnalyzer

class CodeAnalyzer:
    def __init__(self, language='python'):
        self.ast_analyzer = ASTAnalyzer(language)
        self.cfg_builder = CFGBuilder(self.ast_analyzer)
        self.pdg_builder = None # Initialized after CFG
        self.dependency_analyzer = DependencyAnalyzer(self.ast_analyzer)

    def analyze(self, code, function_name):
        # 1. Parse AST
        tree = self.ast_analyzer.parse(code)
        if not tree:
            return {"error": "Could not parse code"}

        # 2. Find Function
        func_node = self.ast_analyzer.get_function_node(tree, function_name)
        if not func_node:
            return {"error": f"Function '{function_name}' not found"}

        # 3. Extract Basic Info
        calls, variables = self.ast_analyzer.extract_dependencies(func_node)
        complexity = self.ast_analyzer.get_complexity(func_node)

        # 4. Build CFG
        cfg = self.cfg_builder.build_cfg(func_node)
        cfg_stats = self.cfg_builder.get_cfg_summary(cfg)

        # 5. Build PDG
        self.pdg_builder = PDGBuilder(self.ast_analyzer, cfg)
        pdg = self.pdg_builder.build_pdg(func_node)
        pdg_stats = self.pdg_builder.get_pdg_summary(pdg)

        # 6. Build Dependency Graph
        # We need repo_root and file_path. For now, we might lack this context in 'analyze' signature.
        # We will update 'analyze' signature or pass placeholders if needed.
        # Ideally, 'analyze' should take file_path.
        # For this step, we will assume file_path is passed or we skip full resolution if not available.
        # Let's update the signature in a separate step or handle it here.
        # Actually, let's just pass None for now and let DependencyAnalyzer handle it gracefully or update signature.
        # Wait, I need to update the signature of analyze to accept file_path.
        
        dependency_graph = self.dependency_analyzer.analyze(None, None, func_node)

        return {
            "function_name": function_name,
            "calls": calls,
            "variables": variables,
            "complexity": complexity,
            "cfg_stats": cfg_stats,
            "pdg_stats": pdg_stats,
            "dependency_graph": dependency_graph,
            "code_structure": f"Cyclomatic Complexity: {complexity}, Calls: {calls}, Vars: {variables}"
        }
