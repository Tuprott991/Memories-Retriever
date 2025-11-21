# Train LongMatrix with large_allmini.yaml config using DDP (multi-GPU)
# Usage: powershell -File train_with_config_ddp.ps1

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   LongMatrix DDP Training with Config File" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$CONFIG_FILE = "finetune/large_allmini.yaml"
$OUTPUT_DIR = "runs/allminilm_large_ddp"
$NUM_GPUS = 4
$MASTER_PORT = 29500

# Check if config file exists
if (-Not (Test-Path $CONFIG_FILE)) {
    Write-Host "❌ Config file not found: $CONFIG_FILE" -ForegroundColor Red
    exit 1
}

# Check if CUDA is available
$cudaAvailable = python -c "import torch; print(torch.cuda.is_available())" 2>$null
if ($cudaAvailable -ne "True") {
    Write-Host "❌ CUDA not available! DDP requires GPUs." -ForegroundColor Red
    exit 1
}

# Check number of available GPUs
$numGpus = python -c "import torch; print(torch.cuda.device_count())" 2>$null
Write-Host "✓ Found $numGpus GPU(s)" -ForegroundColor Green

if ([int]$numGpus -lt $NUM_GPUS) {
    Write-Host "⚠️  Warning: Requested $NUM_GPUS GPUs but only $numGpus available" -ForegroundColor Yellow
    $NUM_GPUS = [int]$numGpus
}

Write-Host "✓ Using config: $CONFIG_FILE" -ForegroundColor Green
Write-Host ""

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - GPUs: $NUM_GPUS" -ForegroundColor White
Write-Host "  - Config File: $CONFIG_FILE" -ForegroundColor White
Write-Host "  - Output Dir: $OUTPUT_DIR" -ForegroundColor White
Write-Host ""

Write-Host "Launching DDP training..." -ForegroundColor Green
Write-Host ""

# Launch torchrun with config file
# Note: You can still override config values via CLI args
torchrun `
  --nproc_per_node=$NUM_GPUS `
  --master_port=$MASTER_PORT `
  finetune/train_longmatrix_update.py `
  --config $CONFIG_FILE `
  --output_dir $OUTPUT_DIR `
  --wandb `
  --wandb_project longmatrix-allmini `
  --wandb_run ddp-$NUM_GPUS-gpus-large

# Example with CLI overrides:
# torchrun --nproc_per_node=4 finetune/train_longmatrix_update.py \
#   --config $CONFIG_FILE \
#   --batch_size 256 \
#   --epochs 10 \
#   --output_dir $OUTPUT_DIR

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host "   Training Completed Successfully!" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output files:" -ForegroundColor Yellow
    Write-Host "  - Best model: $OUTPUT_DIR/best.pt" -ForegroundColor White
    Write-Host "  - Config: $OUTPUT_DIR/config_used.yaml" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Red
    Write-Host "   Training Failed!" -ForegroundColor Red
    Write-Host "=====================================================" -ForegroundColor Red
    exit 1
}
