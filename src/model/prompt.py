class PromptBuilder:
    def __init__(self):
        pass

    def build_prompt(self, code, analysis_result=None, retrieved_exemplars=None):
        """
        Constructs the prompt for the model.
        """
        
        struct_info = ""
        if analysis_result and "error" not in analysis_result:
            struct_info = f"""
### Structure:
Complexity: {analysis_result.get('complexity', 'N/A')}
Calls: {', '.join(analysis_result.get('calls', []))}
Variables: {', '.join(analysis_result.get('variables', []))}
CFG Nodes: {analysis_result.get('cfg_stats', {}).get('nodes', 0)}
PDG Data Deps: {analysis_result.get('pdg_stats', {}).get('data_dependencies', 0)}
"""

        exemplars_text = ""
        if retrieved_exemplars:
            exemplars_text = "### Similar Examples:\n"
            for i, ex in enumerate(retrieved_exemplars):
                exemplars_text += f"Example {i+1}:\nCode:\n{ex.get('code')}\nSummary:\n{ex.get('summary')}\n\n"

        prompt = f"{exemplars_text}### Code:\n{code}\n{struct_info}\n### Summary:\n"
        return prompt
