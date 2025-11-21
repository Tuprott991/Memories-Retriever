# MSMARCO v2.1 Training Guide for LongMatrix

This guide explains how to train the LongMatrix model using MSMARCO v2.1 dataset from HuggingFace with distributed training (DDP) support.

## Overview

The updated `train_longmatrix_update.py` script now supports:
- **MSMARCO v2.1** dataset loading from HuggingFace
- **Hard negatives mining** using BM25, M3 (semantic), or combo methods from `data.py`
- **Distributed Data Parallel (DDP)** training with torchrun for multi-GPU setups
- Backward compatibility with TSV file format

## Installation

### Required Packages

```bash
# Core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers datasets sentence-transformers faiss-cpu
pip install numpy tqdm pyyaml wandb

# For BM25 negatives (choose one)
pip install rank-bm25  # Fallback option (no Java required)
# OR
pip install pyserini   # Recommended (requires JDK 21+)

# Optional: Flash Attention for faster training
pip install flash-attn --no-build-isolation
```

## Training Modes

### 1. Single GPU Training with MSMARCO v2.1

```bash
python finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --msmarco_train_split train \
  --msmarco_dev_split validation \
  --max_train_rows 100000 \
  --neg_method m3 \
  --k_neg 7 \
  --batch_size 64 \
  --epochs 3 \
  --lr 2e-4 \
  --output_dir runs/msmarco_m3 \
  --wandb \
  --wandb_project longmatrix-msmarco
```

### 2. Multi-GPU DDP Training with torchrun

For 4 GPUs:

```bash
torchrun --nproc_per_node=4 --master_port=29500 \
  finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --msmarco_train_split train \
  --msmarco_dev_split validation \
  --max_train_rows 500000 \
  --neg_method combo \
  --k_neg_bm25 3 \
  --k_neg_m3 4 \
  --batch_size 32 \
  --accum_steps 2 \
  --epochs 3 \
  --lr 2e-4 \
  --output_dir runs/msmarco_ddp \
  --wandb
```

**torchrun parameters:**
- `--nproc_per_node`: Number of GPUs per node
- `--master_port`: Port for communication (change if occupied)

### 3. Traditional TSV File Training

```bash
python finetune/train_longmatrix_update.py \
  --data_source tsv \
  --train_tsv data/processed/train.tsv \
  --dev_tsv data/processed/dev.tsv \
  --neg_per_sample 7 \
  --batch_size 64 \
  --epochs 3 \
  --output_dir runs/tsv_training
```

## Negative Mining Methods

### Random Negatives (Fastest)
```bash
--neg_method random \
--k_neg 7
```

### BM25 Lexical Negatives
```bash
--neg_method bm25 \
--k_neg 7 \
--bm25_engine rankbm25 \
--bm25_pool_limit 200000
```

For Pyserini (requires Java):
```bash
--neg_method bm25 \
--bm25_engine pyserini \
--bm25_language en \
--bm25_threads 8
```

### M3 Semantic Negatives (Best Quality)
```bash
--neg_method m3 \
--k_neg 7 \
--m3_model BAAI/bge-m3 \
--m3_bs 64 \
--m3_pool_limit 100000 \
--save_embeds
```

### Combo: BM25 + M3 (Recommended)
```bash
--neg_method combo \
--k_neg_bm25 3 \
--k_neg_m3 4 \
--bm25_engine rankbm25 \
--m3_model BAAI/bge-m3 \
--save_embeds
```

## Key Arguments

### Data Source Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--data_source` | `tsv` | Data source: `tsv` or `msmarco` |
| `--msmarco_train_split` | `train` | MSMARCO train split name |
| `--msmarco_dev_split` | `validation` | MSMARCO dev split name |
| `--msmarco_streaming` | False | Use streaming mode for MSMARCO |
| `--hf_cache_dir` | None | HuggingFace cache directory |
| `--max_train_rows` | None | Limit training samples |

### Negative Mining Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--neg_method` | `random` | Method: `random`, `m3`, `bm25`, `combo` |
| `--k_neg` | 7 | Number of negatives per query |
| `--m3_model` | `BAAI/bge-m3` | M3 model for semantic negatives |
| `--m3_pool_limit` | 100000 | Limit positives for M3 index |
| `--bm25_engine` | `rankbm25` | BM25 backend: `pyserini` or `rankbm25` |
| `--bm25_pool_limit` | 200000 | Limit positives for BM25 index |
| `--save_embeds` | False | Cache M3 embeddings to disk |

### Training Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--batch_size` | 64 | Training batch size per GPU |
| `--accum_steps` | 1 | Gradient accumulation steps |
| `--epochs` | 1 | Number of training epochs |
| `--lr` | 2e-4 | Learning rate |
| `--dtype` | `bf16` | Mixed precision: `fp32`, `fp16`, `bf16` |
| `--grad_ckpt` | False | Enable gradient checkpointing |
| `--torch_compile` | False | Enable torch.compile |

### DDP Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--ddp` | Auto-detect | Enable DDP (auto-detected with torchrun) |

## Example Workflows

### Quick Test with Small Dataset
```bash
python finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --max_train_rows 10000 \
  --neg_method random \
  --batch_size 32 \
  --epochs 1 \
  --output_dir runs/test
```

### Production Training (4 GPUs)
```bash
torchrun --nproc_per_node=4 \
  finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --max_train_rows 1000000 \
  --neg_method combo \
  --k_neg_bm25 4 \
  --k_neg_m3 4 \
  --m3_pool_limit 150000 \
  --bm25_pool_limit 250000 \
  --save_embeds \
  --batch_size 32 \
  --accum_steps 2 \
  --epochs 5 \
  --lr 2e-4 \
  --weight_decay 0.01 \
  --lambda_distill 1.0 \
  --lambda_ortho 1e-3 \
  --ema 0.999 \
  --dtype bf16 \
  --grad_ckpt \
  --late_interaction \
  --topk_q 4 \
  --topk_d 1 \
  --output_dir runs/production \
  --wandb \
  --wandb_project longmatrix-prod
```

### Resume from Checkpoint
```bash
python finetune/train_longmatrix_update.py \
  --data_source msmarco \
  --resume runs/production/best.pt \
  --epochs 3 \
  --output_dir runs/production_continued
```

## Performance Tips

1. **Memory Optimization:**
   - Use `--grad_ckpt` for gradient checkpointing
   - Reduce `--batch_size` and increase `--accum_steps`
   - Set `--m3_pool_limit` and `--bm25_pool_limit` to limit index size

2. **Speed Optimization:**
   - Use `--dtype bf16` on Ampere GPUs (A100, RTX 3090+)
   - Enable `--torch_compile` (PyTorch 2.0+)
   - Use `--allow_tf32` for faster matmul
   - Set `--num_workers 4` for faster data loading

3. **Quality Optimization:**
   - Use `--neg_method combo` for best negatives
   - Enable `--ema 0.999` for stable training
   - Use `--lambda_distill 1.0` to distill from teacher model
   - Enable `--late_interaction` for ColBERT-style matching

## Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size and use gradient accumulation
--batch_size 16 --accum_steps 4 --grad_ckpt
```

### Pyserini Import Error
```bash
# Install Java and Pyserini, or use rank-bm25 fallback
--bm25_engine rankbm25
```

### DDP Hangs or Crashes
```bash
# Check NCCL environment
export NCCL_DEBUG=INFO
export NCCL_IB_DISABLE=1  # If using InfiniBand

# Reduce number of workers to avoid deadlock
--num_workers 0
```

### MSMARCO Dataset Loading Issues
```bash
# Use streaming mode for large datasets
--msmarco_streaming

# Or specify cache directory
--hf_cache_dir /path/to/cache
```

## Output Files

The training script produces:
- `config_used.yaml`: Configuration used for training
- `best.pt`: Best model checkpoint based on dev metrics
- `epoch{N}.pt`: Checkpoint after each epoch
- `train_triplets_cache.json`: Cached training triplets (DDP mode)
- `emb_cache/`: Cached M3 embeddings (if `--save_embeds`)
- `bm25_index/`: BM25 index files (if using Pyserini)

## Monitoring with W&B

Enable Weights & Biases logging:
```bash
--wandb \
--wandb_project my-project \
--wandb_run my-run-name
```

Metrics logged:
- Training loss per step
- Dev Recall@10, MRR@10, nDCG@10
- Learning rate schedule
- Component losses (retrieval, distillation, entropy, orthogonal)

## Next Steps

After training:
1. Use the best checkpoint for inference
2. Export FAISS index with `--export_after_train`
3. Integrate into your retrieval pipeline
4. Fine-tune further with domain-specific data

## References

- [MSMARCO Dataset](https://microsoft.github.io/msmarco/)
- [BGE-M3 Model](https://huggingface.co/BAAI/bge-m3)
- [PyTorch DDP Tutorial](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [Torchrun Documentation](https://pytorch.org/docs/stable/elastic/run.html)
