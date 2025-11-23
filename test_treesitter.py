import tree_sitter
import tree_sitter_python

print("Testing 2 args...")
try:
    tree_sitter.Language(tree_sitter_python.language(), 'python')
    print("Success 2 args")
except Exception as e:
    print(f"Fail 2 args: {e}")

print("Testing 1 arg...")
try:
    tree_sitter.Language(tree_sitter_python.language())
    print("Success 1 arg")
except Exception as e:
    print(f"Fail 1 arg: {e}")
