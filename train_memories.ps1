# Quick Start: Train Memories Retriever Model
# This script automates the entire training pipeline

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   Memories Retriever Model Training Pipeline" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Convert data
Write-Host "[Step 1/3] Converting queries.json to TSV format..." -ForegroundColor Yellow
python finetune/data_converter.py --input data/queries.json --output_dir data/processed

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Data conversion failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[Step 2/3] Checking environment..." -ForegroundColor Yellow

# Check if conda env is active
$condaEnv = $env:CONDA_DEFAULT_ENV
if ($condaEnv) {
    Write-Host "  ✓ Conda environment: $condaEnv" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Warning: No conda environment detected" -ForegroundColor Yellow
    Write-Host "    Consider activating your environment first:" -ForegroundColor Yellow
    Write-Host "    conda activate vertexai" -ForegroundColor Gray
}

# Check GPU availability
Write-Host "  Checking CUDA availability..." -ForegroundColor Gray
python -c "import torch; print('  ✓ CUDA available:', torch.cuda.is_available()); print('  ✓ GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)"

Write-Host ""
Write-Host "[Step 3/3] Starting training..." -ForegroundColor Yellow
Write-Host "  Config: finetune/config_memories.yaml" -ForegroundColor Gray
Write-Host "  Output: runs/memories_retriever/" -ForegroundColor Gray
Write-Host ""

# Start training
python finetune/run_longmatrix.py --config finetune/config_memories.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host "   Training completed successfully!" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Model saved to: runs/memories_retriever/" -ForegroundColor Cyan
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Check training logs in runs/memories_retriever/" -ForegroundColor Gray
    Write-Host "  2. Test your model with queries" -ForegroundColor Gray
    Write-Host "  3. Deploy for production use" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "Training failed! Check the error messages above." -ForegroundColor Red
    exit 1
}
