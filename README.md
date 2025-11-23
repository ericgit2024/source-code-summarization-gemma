# Source Code Summarization with Gemma

A comprehensive code summarization system that leverages fine-tuned Google Gemma models, structural program analysis (AST, CFG, PDG), and RAG to generate high-quality summaries of source code functions.

## 🌟 Features

- **Structural Analysis**: Extracts AST, CFG, and PDG information using tree-sitter
- **Fine-tuned Gemma Model**: Uses Q-LoRA for efficient fine-tuning on custom datasets
- **RAG Integration**: Retrieves similar code examples to improve summary quality
- **Dependency Graph**: Visualizes inter-function dependencies across files
- **Streamlit UI**: Interactive interface for analyzing GitHub repositories
- **Multi-language Support**: Python, Java, JavaScript (extensible)
- **Comprehensive Metrics**: BLEU, ROUGE-L, METEOR, and BERTScore evaluation

## 📋 Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended for training)
- Hugging Face account and token (for accessing Gemma models)
- Git installed on your system

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Source Code Summarization - Gemma"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: If you encounter issues with `tree-sitter` or `bitsandbytes`, you may need to install build tools for your platform.

### 3. Set Up Hugging Face Token

You'll need a Hugging Face token to access the Gemma model:

1. Create an account at [huggingface.co](https://huggingface.co)
2. Request access to the [Gemma model](https://huggingface.co/google/gemma-2b-it)
3. Create a token in your [settings](https://huggingface.co/settings/tokens)
4. Set the environment variable:

**Windows (PowerShell):**
```powershell
$env:HF_TOKEN = "your_token_here"
```

**Linux/Mac:**
```bash
export HF_TOKEN="your_token_here"
```

### 4. Prepare Your Dataset

Your dataset should be in JSONL format with the following structure:

```json
{"code": "def add(a, b):\n    return a + b", "summary": "Returns the sum of two numbers", "func_name": "add"}
{"code": "def multiply(x, y):\n    return x * y", "summary": "Returns the product of two numbers", "func_name": "multiply"}
```

The repository includes a sample dataset: `code_summary_dataset.jsonl`

### 5. Preprocess the Dataset

Add structural analysis information to your dataset:

```bash
python src/data/preprocess.py --input_file code_summary_dataset.jsonl --output_file processed_dataset.jsonl
```

This will:
- Analyze each code snippet using tree-sitter
- Extract complexity, function calls, variables, CFG/PDG statistics
- Create a structured prompt format for training

### 6. Train the Model

Start fine-tuning the Gemma model:

```bash
python src/model/train.py --dataset_path processed_dataset.jsonl --epochs 3
```

**Training Parameters:**
- `--dataset_path`: Path to the preprocessed JSONL file
- `--epochs`: Number of training epochs (default: 1)

**Expected Output:**
- Progress logs every 10 steps
- Model checkpoints saved to `outputs/` directory
- Final model saved after training completes

**GPU Requirements:**
- Minimum: 8GB VRAM (using 4-bit quantization)
- Recommended: 16GB+ VRAM for faster training

> **Note**: Training on CPU is extremely slow and not recommended.

### 7. Run the Streamlit App

After training, launch the interactive interface:

```bash
streamlit run app.py
```

**Using the App:**

1. **Load Model** (Sidebar):
   - Enter your model name: `google/gemma-2b-it`
   - Enter adapter path: `outputs/checkpoint-60` (or your latest checkpoint)
   - Paste your HF token
   - Click "Load Model"

2. **Enable RAG** (Optional):
   - Check "Enable RAG"
   - Upload `code_summary_dataset.jsonl` for indexing
   - Click "Index Codebase"

3. **Analyze Code**:
   - Enter a GitHub repository URL (e.g., `https://github.com/psf/requests`)
   - Enter a function name (e.g., `get`)
   - Click "Analyze and Summarize"

4. **View Results**:
   - Code preview
   - Structural analysis (complexity, calls, variables, CFG/PDG stats)
   - Dependency graph visualization
   - Retrieved exemplars (if RAG enabled)
   - Generated summary

## 📁 Project Structure

```
Source Code Summarization - Gemma/
│
├── src/
│   ├── analysis/          # Static analysis tools
│   │   ├── analyzer.py    # Main CodeAnalyzer class
│   │   ├── ast_utils.py   # AST parsing with tree-sitter
│   │   ├── cfg_builder.py # Control Flow Graph
│   │   ├── pdg_builder.py # Program Dependence Graph
│   │   └── dependency_analyzer.py # Inter-function dependencies
│   │
│   ├── data/             # Dataset processing
│   │   └── preprocess.py # Add structural features
│   │
│   ├── model/            # Model training and inference
│   │   ├── train.py      # Fine-tuning script
│   │   ├── inference.py  # Model inference engine
│   │   ├── prompt.py     # Prompt builder
│   │   └── rag.py        # RAG retrieval engine
│   │
│   ├── evaluation/       # Metrics and evaluation
│   │   └── metrics.py    # BLEU, ROUGE, METEOR, BERTScore
│   │
│   └── utils/            # Utilities
│       └── repo_manager.py # Git repository management
│
├── notebooks/
│   └── fine_tune_gemma.ipynb # Colab-ready training notebook
│
├── app.py                # Streamlit frontend
├── requirements.txt      # Python dependencies
├── code_summary_dataset.jsonl # Sample dataset
└── README.md             # This file
```

## 🔧 Advanced Usage

### Custom Model Configuration

Edit the training parameters in `src/model/train.py`:

```python
# LoRA Configuration
peft_config = LoraConfig(
    r=8,                    # Rank (higher = more parameters)
    lora_alpha=16,          # Scaling factor
    lora_dropout=0.05,      # Dropout rate
    target_modules=[...]    # Modules to fine-tune
)

# Training Arguments
training_args = TrainingArguments(
    per_device_train_batch_size=2,  # Batch size
    learning_rate=2e-4,              # Learning rate
    num_train_epochs=3,              # Epochs
    # ... more parameters
)
```

### Using Different Models

You can use other Gemma variants or compatible models:

```python
# In src/model/train.py
trainer = ModelTrainer(
    model_name="google/gemma-7b-it",  # Larger model
    output_dir="outputs_7b"
)
```

### Command-Line Inference

You can also generate summaries via command line:

```python
from src.model.inference import InferenceEngine

engine = InferenceEngine("google/gemma-2b-it", "outputs/checkpoint-60", hf_token="your_token")
engine.load_model()

prompt = "### Code:\ndef factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n### Summary:\n"
summary = engine.generate(prompt)
print(summary)
```

## 📊 Evaluation

To evaluate your model on a test set:

```python
from src.evaluation.metrics import MetricsCalculator

calculator = MetricsCalculator()
predictions = ["Summary 1", "Summary 2"]
references = ["Reference 1", "Reference 2"]

metrics = calculator.calculate_metrics(predictions, references)
print(metrics)
# Output: {'bleu': 0.xx, 'rouge_l': 0.xx, 'meteor': 0.xx, 'bertscore_f1': 0.xx}
```

## 🐛 Troubleshooting

### Issue: `tree-sitter` Language Error

If you see errors about `tree_sitter.Language`:

1. Check your tree-sitter version: `pip show tree-sitter`
2. The newer API (v0.20.0+) uses a different initialization:
   ```python
   import tree_sitter_python as tspython
   language = tspython.language()
   ```

### Issue: CUDA Out of Memory

Solutions:
- Reduce `per_device_train_batch_size` in `train.py`
- Increase `gradient_accumulation_steps`
- Use a smaller model (gemma-2b instead of gemma-7b)
- Enable gradient checkpointing

### Issue: Hugging Face Token Error

Make sure:
- You've accepted the Gemma license on Hugging Face
- Your token has read permissions
- The environment variable is set correctly

### Issue: Module Import Errors

Add the `src` directory to your Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

Or in Python:
```python
import sys
sys.path.append('src')
```

## 📝 License

[Specify your license here]

## 🙏 Acknowledgments

- Google for the Gemma model
- Hugging Face for the transformers and PEFT libraries
- tree-sitter for the parsing infrastructure

## 📧 Contact

[Your contact information]

---

**Happy Code Summarizing! 🚀**
