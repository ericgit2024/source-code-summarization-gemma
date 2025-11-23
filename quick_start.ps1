# Quick Start Script for Code Summarization with Gemma
# This script automates the setup and training process

Write-Host "=== Code Summarization - Gemma Quick Start ===" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Prompt for HF token
Write-Host "`nHugging Face Token Setup" -ForegroundColor Yellow
Write-Host "You need a Hugging Face token to access the Gemma model."
Write-Host "Get your token from: https://huggingface.co/settings/tokens"
$hf_token = Read-Host "Enter your Hugging Face token"
$env:HF_TOKEN = $hf_token

# Check if dataset exists
if (-not (Test-Path "code_summary_dataset.jsonl")) {
    Write-Host "`nWARNING: code_summary_dataset.jsonl not found!" -ForegroundColor Red
    Write-Host "Please ensure your dataset is in the project root directory."
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Preprocess dataset
Write-Host "`nPreprocessing dataset..." -ForegroundColor Yellow
python src/data/preprocess.py --input_file code_summary_dataset.jsonl --output_file processed_dataset.jsonl

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Preprocessing failed!" -ForegroundColor Red
    exit 1
}

# Ask about training
Write-Host "`nDataset preprocessed successfully!" -ForegroundColor Green
$train = Read-Host "Do you want to start training now? (y/n)"

if ($train -eq "y") {
    $epochs = Read-Host "Enter number of epochs (default: 3)"
    if ([string]::IsNullOrWhiteSpace($epochs)) {
        $epochs = 3
    }
    
    Write-Host "`nStarting training with $epochs epochs..." -ForegroundColor Yellow
    Write-Host "This may take several hours depending on your GPU..." -ForegroundColor Cyan
    python src/model/train.py --dataset_path processed_dataset.jsonl --epochs $epochs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nTraining completed successfully!" -ForegroundColor Green
        Write-Host "Model saved to outputs/" -ForegroundColor Green
    } else {
        Write-Host "`nERROR: Training failed!" -ForegroundColor Red
        exit 1
    }
}

# Ask about running app
Write-Host "`n"
$run_app = Read-Host "Do you want to launch the Streamlit app? (y/n)"

if ($run_app -eq "y") {
    Write-Host "`nLaunching Streamlit app..." -ForegroundColor Yellow
    Write-Host "The app will open in your browser." -ForegroundColor Cyan
    streamlit run app.py
}

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "To manually run the app later, use: streamlit run app.py" -ForegroundColor Cyan
