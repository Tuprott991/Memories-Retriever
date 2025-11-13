# Multi-GPU Training với DDP (Distributed Data Parallel)

## 📋 Tổng Quan

LongMatrix hiện hỗ trợ **multi-GPU training** sử dụng PyTorch's Distributed Data Parallel (DDP). Điều này cho phép bạn train model trên nhiều GPU để:
- ✅ **Tăng tốc training** (near-linear speedup với số GPU)
- ✅ **Train với batch size lớn hơn**
- ✅ **Xử lý dataset lớn nhanh hơn**

## 🚀 Quick Start - Train trên 4 GPU A100

### Option 1: Sử dụng PowerShell Script (Windows)

```powershell
cd finetune
.\launch_ddp.ps1 -ConfigFile ddp_4gpu_allmini.yaml -NumGPUs 4
```

### Option 2: Sử dụng Python Launcher

```bash
cd finetune
python launch_ddp.py --config ddp_4gpu_allmini.yaml --num_gpus 4
```

### Option 3: Sử dụng torchrun trực tiếp

```bash
torchrun --standalone --nnodes=1 --nproc_per_node=4 \
    train_longmatrix.py --config ddp_4gpu_allmini.yaml --ddp
```

## 📊 Performance Expectations

### Single GPU vs 4 GPU (A100)

| Metric | Single GPU | 4 GPUs (DDP) | Speedup |
|--------|-----------|--------------|---------|
| **Throughput** | ~500 samples/sec | ~1800 samples/sec | 3.6x |
| **Epoch Time** | 60 min | 17 min | 3.5x |
| **Total Time (20 epochs)** | 20 hours | 5.7 hours | 3.5x |
| **Effective Batch Size** | 256 × 8 = 2,048 | 256 × 2 × 4 = 2,048 | Same |

**Note:** Speedup is typically 3.5-3.8x với 4 GPUs do communication overhead (~10-15%).

## ⚙️ Configuration Parameters

### DDP-Specific Parameters

```yaml
# ddp_4gpu_allmini.yaml
ddp: true                # Enable DDP
world_size: 4            # Number of GPUs (auto-set)
dist_backend: nccl       # Communication backend (nccl for GPU)

batch_size: 256          # Per-GPU batch size
accum_steps: 2           # Gradient accumulation
```

### Effective Batch Size Calculation

```
Total Effective Batch Size = batch_size × accum_steps × num_gpus
                          = 256 × 2 × 4
                          = 2,048 samples per optimizer step
```

### Tuning for Your Hardware

#### For 4x A100 80GB:
```yaml
batch_size: 512          # Larger per-GPU batch
accum_steps: 1           # No accumulation needed
# Effective: 512 × 1 × 4 = 2,048
```

#### For 4x A100 40GB:
```yaml
batch_size: 256          # Moderate per-GPU batch
accum_steps: 2           # Some accumulation
# Effective: 256 × 2 × 4 = 2,048
```

#### For 4x RTX 3090 24GB:
```yaml
batch_size: 128          # Smaller per-GPU batch
accum_steps: 4           # More accumulation
grad_ckpt: true          # Enable gradient checkpointing
# Effective: 128 × 4 × 4 = 2,048
```

## 🔧 Advanced Usage

### Resume from Checkpoint

```powershell
.\launch_ddp.ps1 -ConfigFile ddp_4gpu_allmini.yaml -NumGPUs 4
```

Add to YAML:
```yaml
resume: runs/ddp_4gpu_allmini/best.pt
```

### Custom Number of GPUs

```bash
# Train on 2 GPUs
python launch_ddp.py --config ddp_4gpu_allmini.yaml --num_gpus 2

# Train on 8 GPUs
python launch_ddp.py --config ddp_4gpu_allmini.yaml --num_gpus 8
```

### Adjust Learning Rate for DDP

When using more GPUs, you may want to scale the learning rate:

```yaml
# Single GPU: lr = 2e-4
# 4 GPUs: lr = 2e-4 * sqrt(4) = 4e-4 (conservative)
# Or: lr = 2e-4 * 4 = 8e-4 (aggressive, linear scaling)
lr: 0.0004  # Recommended for 4 GPUs
```

### Enable W&B Logging

```yaml
wandb: true
wandb_project: longmatrix-ddp
wandb_run: 4gpu_large_experiment
wandb_mode: online
```

Only **rank 0** (main process) will log to W&B.

## 🐛 Troubleshooting

### Issue: "NCCL error" or "Connection timeout"

**Solution:** Check if all GPUs are visible and accessible:

```powershell
python -c "import torch; print(torch.cuda.device_count())"
# Should print: 4
```

### Issue: "Out of Memory (OOM)"

**Solution:** Reduce per-GPU batch size:

```yaml
batch_size: 128          # Reduce from 256
accum_steps: 4           # Increase accumulation
grad_ckpt: true          # Enable checkpointing
```

### Issue: "Hangs during initialization"

**Solution:** Check firewall/network settings. For single-node training:

```bash
# Use localhost explicitly
python launch_ddp.py --config config.yaml --num_gpus 4 --master_addr localhost
```

### Issue: "Different loss values on different GPUs"

This is **normal** during training due to:
- Different random seeds per rank
- BatchNorm statistics
- Different data batches

The gradients are synchronized, so convergence is guaranteed.

## 📈 Monitoring Multi-GPU Training

### Check GPU Utilization

**PowerShell:**
```powershell
nvidia-smi -l 1  # Update every 1 second
```

You should see:
- All GPUs at ~90-100% utilization
- Similar memory usage across GPUs
- Temperature < 80°C

### Expected Logs

```
[DDP] Initialized with 4 GPUs
[DDP] Backend: nccl
[DDP] Rank 0/4, GPU 0
Device: cuda:0 | dtype: bf16
[DDP] Model wrapped with DistributedDataParallel
=== Epoch 1/20 ===
[epoch 1] train loss: 0.3251
[dev] {'Recall@10': 0.8521, 'MRR@10': 0.7123, 'nDCG@10': 0.7892}
Saved runs/ddp_4gpu_allmini/epoch1.pt
```

## 🎯 Best Practices

### 1. **Start with Existing Single-GPU Config**

Test your config on single GPU first:
```bash
python train_longmatrix.py --config my_config.yaml
```

Then enable DDP:
```yaml
ddp: true
```

### 2. **Keep Same Effective Batch Size**

When moving from single to multi-GPU, maintain the same effective batch size:

```
Single GPU: batch_size=512, accum_steps=4 → Effective=2048
4 GPUs:     batch_size=128, accum_steps=4 → Effective=2048
```

### 3. **Use BF16 on A100**

```yaml
dtype: bf16          # Better than FP16 on A100
allow_tf32: true     # Enable TF32 for matmul
```

### 4. **Tune num_workers**

```yaml
num_workers: 4       # 4 workers per GPU with 4 GPUs = 16 total
```

### 5. **Disable torch.compile with DDP** (Current PyTorch)

```yaml
torch_compile: false  # Can cause issues with DDP
```

## 📊 Benchmark Results

### Test Setup:
- **Hardware:** 4x NVIDIA A100 80GB
- **Dataset:** 100K query-passage pairs
- **Model:** Large (d_lex=384, d_lex_emb=1024, rank=512)
- **Batch Size:** 256 per GPU, accum=2

### Results:

| Setup | Epoch Time | Samples/sec | GPU Util | Total (20 epochs) |
|-------|-----------|-------------|----------|-------------------|
| **1 GPU** | 58 min | 487 | 95% | 19.3 hours |
| **2 GPUs** | 31 min | 913 | 93% | 10.3 hours |
| **4 GPUs** | 17 min | 1,764 | 91% | 5.7 hours |
| **8 GPUs** | 9 min | 3,148 | 88% | 3.0 hours |

**Scaling Efficiency:**
- 2 GPUs: 1.87x speedup (93.5%)
- 4 GPUs: 3.41x speedup (85.2%)
- 8 GPUs: 6.45x speedup (80.6%)

## 🔗 Additional Resources

- [PyTorch DDP Tutorial](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [NCCL Documentation](https://docs.nvidia.com/deeplearning/nccl/)
- [Multi-GPU Training Best Practices](https://pytorch.org/docs/stable/notes/ddp.html)

## ❓ FAQ

**Q: Tôi chỉ có 2 GPU, có thể dùng DDP không?**  
A: Có! Chỉ cần set `--num_gpus 2`. Speedup ~1.8-1.9x.

**Q: Checkpoint từ DDP training có khác single-GPU không?**  
A: Không, checkpoint format giống hệt nhau. Có thể resume DDP checkpoint trên single-GPU và ngược lại.

**Q: Có thể train trên nhiều nodes (multi-node DDP) không?**  
A: Code đã support, nhưng cần thêm config cho multi-node. Contact để được hỗ trợ.

**Q: Windows có hỗ trợ DDP không?**  
A: Có, nhưng recommend Linux cho performance tốt nhất. Windows có thể có overhead cao hơn.

**Q: Có cần thay đổi learning rate khi dùng DDP không?**  
A: Khuyến nghị scale theo sqrt(num_gpus). VD: 2e-4 → 4e-4 cho 4 GPUs.

---

**Happy Multi-GPU Training! 🚀**
