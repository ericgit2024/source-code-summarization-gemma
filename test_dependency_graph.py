import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.ast_utils import ASTAnalyzer
from src.analysis.dependency_analyzer import DependencyAnalyzer

def test_dependency_graph():
    code = """
import os
from utils import helper

def my_func():
    x = os.path.join("a", "b")
    y = helper.do_something()
    local_call()
    return x

def local_call():
    pass
"""
    analyzer = ASTAnalyzer('python')
    tree = analyzer.parse(code)
    func_node = analyzer.get_function_node(tree, 'my_func')
    
    dep_analyzer = DependencyAnalyzer(analyzer)
    # We pass the root node of the tree as a proxy for file_path context if needed, 
    # but our current implementation re-parses or walks up. 
    # Wait, my implementation walks up from func_node.
    
    graph = dep_analyzer.analyze(None, None, func_node)
    
    print("Nodes:", len(graph['nodes']))
    print("Edges:", len(graph['edges']))
    
    for node in graph['nodes']:
        print(f"Node: {node['id']} ({node['type']}) - {node['label']}")
        
    for edge in graph['edges']:
        print(f"Edge: {edge['source']} -> {edge['target']} ({edge['relation']})")

    # Assertions
    node_ids = [n['id'] for n in graph['nodes']]
    assert "func:my_func" in node_ids
    assert "mod:os" in node_ids or "mod:os.path" in node_ids # Depending on how we handle it
    # Actually, os.path.join -> os is imported.
    # My logic: "os.path.join" call. Import "os".
    # "os" alias is "os". "os.path.join" starts with "os.". Match!
    
    assert "mod:utils.helper" in node_ids
    assert "func:local_call" in node_ids

if __name__ == "__main__":
    try:
        test_dependency_graph()
        print("Test Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
