import os
import git
import shutil
import tempfile
from pathlib import Path

class RepoManager:
    def __init__(self, base_dir=None):
        # Use system temp directory if no base_dir provided
        if base_dir is None:
            # Create a subdirectory in the system temp folder
            self.base_dir = os.path.join(tempfile.gettempdir(), "code_summarizer_repos")
        else:
            self.base_dir = base_dir
            
        if not os.path.exists(self.base_dir):
            try:
                os.makedirs(self.base_dir)
            except OSError as e:
                # Fallback to a purely random temp dir if the named one fails
                print(f"Warning: Could not create {self.base_dir}, using random temp dir. Error: {e}")
                self.base_dir = tempfile.mkdtemp()

    def clone_repo(self, repo_url):
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_dir = os.path.join(self.base_dir, repo_name)
        
        if os.path.exists(target_dir):
            # For simplicity, remove and re-clone to ensure fresh state
            # In production, git pull might be better
            try:
                shutil.rmtree(target_dir)
            except PermissionError:
                return None, f"Error: Could not remove existing directory {target_dir}. Please close any open files."
            except Exception as e:
                return None, f"Error removing directory: {e}"

        try:
            print(f"Cloning {repo_url} to {target_dir}...")
            git.Repo.clone_from(repo_url, target_dir)
            return target_dir, None
        except Exception as e:
            return None, str(e)

    def find_function(self, repo_dir, function_name):
        # Naive search: look for "def function_name" or similar strings in files
        # A better approach would be to use tree-sitter on every file, but that's slow.
        # We will use a grep-like approach to narrow down candidates, then parse.
        
        candidates = []
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                if file.endswith(('.py', '.java', '.js')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Simple heuristic check
                            if function_name in content:
                                candidates.append(file_path)
                    except Exception:
                        continue
        
        return candidates
