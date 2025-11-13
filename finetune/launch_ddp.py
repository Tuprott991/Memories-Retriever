#!/usr/bin/env python3
"""
Multi-GPU Training Launcher for LongMatrix
Launches training on multiple GPUs using PyTorch's torchrun

Usage:
    python launch_ddp.py --config config.yaml --num_gpus 4
"""
import argparse
import os
import sys
import subprocess
import shlex

def main():
    parser = argparse.ArgumentParser(description='Launch multi-GPU training')
    parser.add_argument('--config', type=str, required=True, help='Path to YAML config file')
    parser.add_argument('--num_gpus', type=int, default=4, help='Number of GPUs to use (default: 4)')
    parser.add_argument('--script', type=str, default='train_longmatrix.py', help='Training script')
    parser.add_argument('--master_addr', type=str, default='localhost', help='Master address')
    parser.add_argument('--master_port', type=int, default=29500, help='Master port')
    parser.add_argument('--dry_run', action='store_true', help='Print command without executing')
    args = parser.parse_args()
    
    print("=" * 60)
    print("LongMatrix Multi-GPU Training Launcher")
    print("=" * 60)
    print()
    
    # Validate files
    if not os.path.exists(args.config):
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        return 1
    
    if not os.path.exists(args.script):
        print(f"ERROR: Training script not found: {args.script}", file=sys.stderr)
        return 1
    
    # Display settings
    print("Configuration:")
    print(f"  Config file: {args.config}")
    print(f"  Training script: {args.script}")
    print(f"  Number of GPUs: {args.num_gpus}")
    print(f"  Master address: {args.master_addr}")
    print(f"  Master port: {args.master_port}")
    print()
    
    # Create log directory for error tracking
    log_dir = os.path.join(os.path.dirname(args.script) or '.', 'ddp_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Build torchrun command with error logging
    cmd = [
        sys.executable, '-m', 'torch.distributed.run',
        '--standalone',
        '--nnodes=1',
        f'--nproc_per_node={args.num_gpus}',
        f'--master_addr={args.master_addr}',
        f'--master_port={args.master_port}',
        f'--log_dir={log_dir}',  # Enable error file logging
        '--redirects=3',         # Redirect stdout/stderr to files
        args.script,
        '--config', args.config,
        '--ddp'
    ]
    
    # Display command
    print("Command to execute:")
    print(' '.join(shlex.quote(x) for x in cmd))
    print()
    
    if args.dry_run:
        print("[DRY RUN] Exiting without execution")
        return 0
    
    print("Starting training...")
    print()
    
    # Set environment variables for better error messages and debugging
    env = os.environ.copy()
    env['TORCH_DISTRIBUTED_DEBUG'] = 'DETAIL'
    env['TORCH_SHOW_CPP_STACKTRACES'] = '1'
    env['NCCL_DEBUG'] = 'WARN'  # Changed from INFO to WARN to reduce noise
    env['PYTHONFAULTHANDLER'] = '1'
    
    # CRITICAL: NCCL configuration for single-node multi-GPU
    # Force NCCL to use local communication only (no network)
    env['NCCL_P2P_LEVEL'] = 'NVL'  # Use NVLink if available, otherwise PCIe
    env['NCCL_SHM_DISABLE'] = '0'   # Enable shared memory
    env['NCCL_IB_DISABLE'] = '1'    # Disable InfiniBand (not available on GCP)
    env['NCCL_SOCKET_IFNAME'] = 'lo'  # Use loopback for any socket communication
    
    # CRITICAL: Unset TORCH_NCCL_ASYNC_ERROR_HANDLING as recommended by NCCL
    # The GCP environment expects this to be unset
    if 'TORCH_NCCL_ASYNC_ERROR_HANDLING' in env:
        del env['TORCH_NCCL_ASYNC_ERROR_HANDLING']
    
    # Execute
    try:
        result = subprocess.run(cmd, env=env)
        exit_code = result.returncode
        
        print()
        if exit_code == 0:
            print("=" * 60)
            print("Training completed successfully!")
            print("=" * 60)
        else:
            print("=" * 60)
            print(f"Training failed with exit code: {exit_code}")
            print("=" * 60)
        
        return exit_code
        
    except Exception as e:
        print(f"ERROR: Failed to launch training: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
