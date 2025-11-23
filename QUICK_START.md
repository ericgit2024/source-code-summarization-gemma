# 🚀 Quick Reference Card

## After Cloning - Complete Setup in 3 Steps

### 1️⃣ Install & Setup (5 minutes)
```powershell
# Install dependencies
pip install -r requirements.txt

# Set your Hugging Face token (get from https://huggingface.co/settings/tokens)
$env:HF_TOKEN = "hf_YOUR_TOKEN_HERE"
```

### 2️⃣ Train the Model (2-4 hours)
```powershell
# Preprocess your dataset
python src/data/preprocess.py --input_file code_summary_dataset.jsonl --output_file processed_dataset.jsonl

# Train the model (requires GPU)
python src/model/train.py --dataset_path processed_dataset.jsonl --epochs 3
```

### 3️⃣ Run the App (30 seconds)
```powershell
streamlit run app.py
```

Then in the UI:
- Enter model: `google/gemma-2b-it`
- Enter adapter path: `outputs/checkpoint-60`
- Paste your HF token
- Click "Load Model"
- Enter GitHub URL and function name
- Click "Analyze and Summarize"

---

## 🎯 Alternative: One-Click Setup
```powershell
.\quick_start.ps1
```
Follow the prompts!

---

## 📊 What Gets Trained?

The model learns to generate summaries using:
- **Code structure** (AST, CFG, PDG)
- **Complexity metrics**
- **Function dependencies**
- **Your custom dataset format**

Input format:
```json
{"code": "def foo():\n    pass", "summary": "Does something", "func_name": "foo"}
```

---

## ⚙️ Key Files

| File | Purpose |
|------|---------|
| `src/data/preprocess.py` | Add structural features to dataset |
| `src/model/train.py` | Fine-tune Gemma with Q-LoRA |
| `app.py` | Streamlit web interface |
| `code_summary_dataset.jsonl` | Your training data |

---

## 🔧 Troubleshooting

**GPU Out of Memory?**
- Reduce batch size in `src/model/train.py` (line 56)
- Use smaller model: `google/gemma-2b-it` instead of `7b`

**Tree-sitter errors?**
- Check version: `pip show tree-sitter`
- See `debug_treesitter.py` for fixes

**Model not loading?**
- Verify HF token has access to Gemma
- Check you accepted the license at https://huggingface.co/google/gemma-2b-it

---

## 📖 Full Documentation

- [README.md](README.md) - Complete documentation
- [TRAINING_GUIDE.md](TRAINING_GUIDE.md) - Step-by-step visual guide with diagrams

---

**That's it! You're ready to train and run the model! 🎉**
