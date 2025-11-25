# Launch DDP Training for LongMatrix with MSMARCO v2.1
# Usage: powershell -File launch_ddp_msmarco.ps1

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   LongMatrix DDP Training with MSMARCO v2.1" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$NUM_GPUS = 4
$MASTER_PORT = 29500
$OUTPUT_DIR = "runs/msmarco_ddp_training"

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

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - GPUs: $NUM_GPUS" -ForegroundColor White
Write-Host "  - Master Port: $MASTER_PORT" -ForegroundColor White
Write-Host "  - Output Dir: $OUTPUT_DIR" -ForegroundColor White
Write-Host ""

# Create output directory
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

# Launch torchrun
Write-Host "Launching DDP training..." -ForegroundColor Green
Write-Host ""

torchrun `
  --nproc_per_node=$NUM_GPUS `
  --master_port=$MASTER_PORT `
  finetune/train_longmatrix_update.py `
  --data_source msmarco `
  --msmarco_train_split train `
  --msmarco_dev_split validation `
  --max_train_rows 500000 `
  --neg_method combo `
  --k_neg_bm25 3 `
  --k_neg_m3 4 `
  --m3_model BAAI/bge-m3 `
  --m3_bs 64 `
  --m3_pool_limit 100000 `
  --bm25_engine rankbm25 `
  --bm25_pool_limit 200000 `
  --save_embeds `
  --batch_size 32 `
  --accum_steps 2 `
  --epochs 3 `
  --lr 2e-4 `
  --weight_decay 0.01 `
  --warmup_steps 1000 `
  --lambda_distill 1.0 `
  --lambda_ortho 1e-3 `
  --lambda_ret 1.0 `
  --ema 0.999 `
  --dtype bf16 `
  --grad_ckpt `
  --late_interaction `
  --topk_q 4 `
  --topk_d 1 `
  --max_len 128 `
  --num_workers 4 `
  --output_dir $OUTPUT_DIR `
  --wandb `
  --wandb_project longmatrix-msmarco `
  --wandb_run ddp-$NUM_GPUS-gpus

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host "   Training Completed Successfully!" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output files:" -ForegroundColor Yellow
    Write-Host "  - Best model: $OUTPUT_DIR/best.pt" -ForegroundColor White
    Write-Host "  - Config: $OUTPUT_DIR/config_used.yaml" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Red
    Write-Host "   Training Failed!" -ForegroundColor Red
    Write-Host "=====================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above." -ForegroundColor Yellow
    exit 1
}
