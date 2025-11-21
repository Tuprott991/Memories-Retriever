# Train LongMatrix with large_allmini.yaml config
# Usage: powershell -File train_with_config.ps1

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   LongMatrix Training with Config File" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$CONFIG_FILE = "finetune/large_allmini.yaml"
$OUTPUT_DIR = "runs/allminilm_large"

# Check if config file exists
if (-Not (Test-Path $CONFIG_FILE)) {
    Write-Host "❌ Config file not found: $CONFIG_FILE" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Using config: $CONFIG_FILE" -ForegroundColor Green
Write-Host ""

# Single GPU training with config
Write-Host "Starting training with config file..." -ForegroundColor Yellow
Write-Host ""

python finetune/train_longmatrix_update.py `
  --config $CONFIG_FILE `
  --output_dir $OUTPUT_DIR

# Note: CLI arguments override config file values
# Example: To override batch size from config:
# python finetune/train_longmatrix_update.py --config $CONFIG_FILE --batch_size 128

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
