import streamlit as st
import os
import sys
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.repo_manager import RepoManager
from src.analysis.analyzer import CodeAnalyzer
from src.model.inference import InferenceEngine
from src.model.prompt import PromptBuilder
from src.model.rag import RAGEngine
from src.evaluation.metrics import MetricsCalculator

st.set_page_config(page_title="SP-RAG Code Summarizer", layout="wide")

st.title("SP-RAG: Structural Prompting + RAG Code Summarizer")
st.markdown("Generate structurally accurate and semantically rich summaries for your code.")

# Sidebar for configuration
with st.sidebar:
    st.header("Model Configuration")
    model_name = st.text_input("Model Name", "google/gemma-2b-it")
    adapter_path = st.text_input("Adapter Path (Optional)", "outputs/checkpoint-60")
    hf_token = st.text_input("Hugging Face Token", type="password", help="Required for gated models")
    
    if st.button("Load Model"):
        with st.spinner("Loading model..."):
            if 'inference_engine' not in st.session_state:
                st.session_state.inference_engine = InferenceEngine(model_name, adapter_path if adapter_path else None, hf_token)
                st.session_state.inference_engine.load_model()
            st.success("Model loaded!")

    st.header("RAG Configuration")
    rag_enabled = st.checkbox("Enable RAG", value=True)
    if rag_enabled:
        if 'rag_engine' not in st.session_state:
            st.session_state.rag_engine = RAGEngine()
        
        uploaded_file = st.file_uploader("Upload Dataset for Indexing (JSONL)", type="jsonl")
        if uploaded_file and st.button("Index Codebase"):
            with st.spinner("Indexing codebase..."):
                data_items = []
                for line in uploaded_file:
                    try:
                        data_items.append(json.loads(line))
                    except:
                        pass
                st.session_state.rag_engine.index_codebase(data_items)
                st.success(f"Indexed {len(data_items)} items.")

# Main Content
repo_url = st.text_input("GitHub Repository URL", "https://github.com/psf/requests")
function_name = st.text_input("Function Name", "get")

if st.button("Analyze and Summarize"):
    if not repo_url or not function_name:
        st.error("Please provide both Repo URL and Function Name.")
    else:
        repo_manager = RepoManager()
        
        with st.spinner(f"Cloning {repo_url}..."):
            repo_dir, error = repo_manager.clone_repo(repo_url)
            
        if error:
            st.error(f"Failed to clone repo: {error}")
        else:
            st.success(f"Cloned to {repo_dir}")
            
            with st.spinner(f"Searching for function '{function_name}'..."):
                candidates = repo_manager.find_function(repo_dir, function_name)
            
            if not candidates:
                st.warning(f"Function '{function_name}' not found in repository.")
            else:
                st.info(f"Found {len(candidates)} candidate files.")
                selected_file = st.selectbox("Select File", candidates)
                
                if selected_file:
                    with open(selected_file, 'r', encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                    
                    st.subheader("Code Preview")
                    st.code(code, language='python')
                    
                    # Analyze
                    analyzer = CodeAnalyzer(language='python')
                    with st.spinner("Running Structural Analysis (AST, CFG, PDG)..."):
                        analysis_result = analyzer.analyze(code, function_name)
                    
                    if "error" in analysis_result:
                        st.error(analysis_result["error"])
                    else:
                        st.subheader("Structural Analysis")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Complexity", analysis_result.get('complexity'))
                        col1.metric("Calls", len(analysis_result.get('calls', [])))
                        col2.metric("Variables", len(analysis_result.get('variables', [])))
                        col3.metric("CFG Nodes", analysis_result.get('cfg_stats', {}).get('nodes', 0))
                        col4.metric("PDG Data Deps", analysis_result.get('pdg_stats', {}).get('data_dependencies', 0))
                        
                        with st.expander("View Analysis Details"):
                            st.json(analysis_result)

                        # Dependency Graph
                        if 'dependency_graph' in analysis_result:
                            st.subheader("Dependency Graph")
                            graph_data = analysis_result['dependency_graph']
                            if graph_data and graph_data.get('nodes'):
                                import graphviz
                                dot = graphviz.Digraph()
                                for node in graph_data['nodes']:
                                    dot.node(node['id'], node['label'], shape=node.get('shape', 'ellipse'), style=node.get('style', ''), fillcolor=node.get('fillcolor', 'white'))
                                for edge in graph_data['edges']:
                                    dot.edge(edge['source'], edge['target'], label=edge.get('relation', ''))
                                st.graphviz_chart(dot)
                            else:
                                st.info("No dependencies found to visualize.")
                        
                        # RAG Retrieval
                        retrieved_exemplars = []
                        if rag_enabled and 'rag_engine' in st.session_state:
                            with st.spinner("Retrieving similar examples..."):
                                retrieved_exemplars = st.session_state.rag_engine.retrieve(code, k=3)
                            
                            if retrieved_exemplars:
                                with st.expander("View Retrieved Exemplars"):
                                    for i, ex in enumerate(retrieved_exemplars):
                                        st.markdown(f"**Example {i+1}**")
                                        st.code(ex.get('code'), language='python')
                                        st.markdown(f"*Summary:* {ex.get('summary')}")
                                        st.divider()
                        
                        # Generate Summary
                        if 'inference_engine' in st.session_state and st.session_state.inference_engine.model:
                            prompt_builder = PromptBuilder()
                            prompt = prompt_builder.build_prompt(code, analysis_result, retrieved_exemplars)
                            
                            with st.spinner("Generating Summary with Gemma..."):
                                summary = st.session_state.inference_engine.generate(prompt)
                                
                            st.subheader("Generated Summary")
                            st.markdown(summary)
                            
                            # Evaluation (Optional)
                            st.subheader("Evaluation")
                            reference_summary = st.text_area("Enter Reference Summary (for evaluation)", "")
                            if reference_summary and st.button("Calculate Metrics"):
                                calculator = MetricsCalculator()
                                metrics = calculator.calculate_metrics([summary], [reference_summary])
                                st.json(metrics)
                        else:
                            st.warning("Model not loaded. Please load the model in the sidebar.")
