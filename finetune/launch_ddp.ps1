# Multi-GPU Training Launcher for LongMatrix
# Launches training on multiple GPUs using PyTorch's torchrun
# Usage: .\launch_ddp.ps1 -ConfigFile config.yaml -NumGPUs 4

param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigFile,
    
    [Parameter(Mandatory=$false)]
    [int]$NumGPUs = 4,
    
    [Parameter(Mandatory=$false)]
    [string]$Script = "train_longmatrix.py",
    
    [Parameter(Mandatory=$false)]
    [string]$MasterAddr = "localhost",
    
    [Parameter(Mandatory=$false)]
    [int]$MasterPort = 29500,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "LongMatrix Multi-GPU Training Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Validate config file
if (-not (Test-Path $ConfigFile)) {
    Write-Host "ERROR: Config file not found: $ConfigFile" -ForegroundColor Red
    exit 1
}

# Validate script
if (-not (Test-Path $Script)) {
    Write-Host "ERROR: Training script not found: $Script" -ForegroundColor Red
    exit 1
}

# Display settings
Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  Config file:  $ConfigFile"
Write-Host "  Training script: $Script"
Write-Host "  Number of GPUs: $NumGPUs"
Write-Host "  Master address: $MasterAddr"
Write-Host "  Master port: $MasterPort"
Write-Host ""

# Build torchrun command
$TorchRunArgs = @(
    "--standalone",
    "--nnodes=1",
    "--nproc_per_node=$NumGPUs",
    "--master_addr=$MasterAddr",
    "--master_port=$MasterPort",
    $Script
)

# Add config from YAML
$PythonArgs = @(
    "--config", $ConfigFile,
    "--ddp"
)

# Combine all arguments
$FullCommand = "torchrun " + ($TorchRunArgs -join " ") + " " + ($PythonArgs -join " ")

Write-Host "Command to execute:" -ForegroundColor Yellow
Write-Host $FullCommand -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN] Exiting without execution" -ForegroundColor Yellow
    exit 0
}

Write-Host "Starting training..." -ForegroundColor Green
Write-Host ""

# Execute
try {
    & torchrun @TorchRunArgs @PythonArgs
    $ExitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($ExitCode -eq 0) {
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "Training completed successfully!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
    } else {
        Write-Host "============================================================" -ForegroundColor Red
        Write-Host "Training failed with exit code: $ExitCode" -ForegroundColor Red
        Write-Host "============================================================" -ForegroundColor Red
    }
    exit $ExitCode
}
catch {
    Write-Host "ERROR: Failed to launch training" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
