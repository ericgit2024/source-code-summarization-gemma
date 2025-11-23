import os
import json
import argparse
from datasets import load_dataset
from src.analysis.analyzer import CodeAnalyzer
from tqdm import tqdm

class DatasetProcessor:
    def __init__(self, language='python'):
        self.analyzer = CodeAnalyzer(language)

    def process_dataset(self, input_file, output_file):
        """
        Reads a JSONL file with 'code' and 'summary' fields.
        Analyzes the code to extract structural info.
        Saves a new JSONL with 'input_text' (structural prompt) and 'target_text' (summary).
        """
        print(f"Processing {input_file}...")
        
        processed_data = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in tqdm(lines):
            try:
                item = json.loads(line)
                code = item.get('code', '')
                summary = item.get('summary', '')
                func_name = item.get('func_name', 'unknown') # Optional
                
                if not code:
                    continue
                    
                # Analyze code
                # Note: We might need to infer function name if not provided, or just analyze the whole block
                # For this script, we assume the code is a function.
                # If func_name is unknown, the analyzer might fail to find the function node if it relies on name.
                # Let's try to parse and find the first function if name is unknown.
                
                analysis_result = self.analyzer.analyze(code, func_name)
                
                if "error" in analysis_result and func_name == 'unknown':
                     # Try to find any function
                     # This requires updating analyzer to support "find first function" or we just skip
                     pass
                
                # Build Structural Prompt
                # Format:
                # ### Code:
                # {code}
                # ### Structure:
                # Complexity: {complexity}
                # Calls: {calls}
                # Variables: {variables}
                # CFG Stats: {cfg_stats}
                # PDG Stats: {pdg_stats}
                # ### Summary:
                
                struct_info = ""
                if "error" not in analysis_result:
                    struct_info = f"""
### Structure:
Complexity: {analysis_result.get('complexity', 'N/A')}
Calls: {', '.join(analysis_result.get('calls', []))}
Variables: {', '.join(analysis_result.get('variables', []))}
CFG Nodes: {analysis_result.get('cfg_stats', {}).get('nodes', 0)}
PDG Data Deps: {analysis_result.get('pdg_stats', {}).get('data_dependencies', 0)}
"""
                
                prompt = f"### Code:\n{code}\n{struct_info}\n### Summary:\n"
                
                processed_data.append({
                    "input_text": prompt,
                    "target_text": summary
                })
                
            except json.JSONDecodeError:
                continue
                
        # Save processed data
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in processed_data:
                f.write(json.dumps(item) + '\n')
                
        print(f"Saved {len(processed_data)} processed items to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="code_summary_dataset.jsonl")
    parser.add_argument("--output_file", type=str, default="processed_dataset.jsonl")
    args = parser.parse_args()
    
    processor = DatasetProcessor()
    processor.process_dataset(args.input_file, args.output_file)
