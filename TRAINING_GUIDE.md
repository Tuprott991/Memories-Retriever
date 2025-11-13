# Training Guide: Memories Retriever Model

## Overview
This guide walks you through training a custom retrieval model for your personal memories using the LongMatrix architecture.

## Data Structure

Your `data/queries.json` contains memory records with:
- **caption**: The memory description (what you want to retrieve)
- **queries**: Natural language queries that should find this memory
- **negatives**: Hard negative examples (similar but different memories)

Example:
```json
{
  "id": "memory_0001",
  "caption": "Leo's 1st birthday party at Grandma's house...",
  "queries": ["Leo's first birthday party", "Show me pictures of Leo turning one", ...],
  "negatives": ["Leo's second birthday party", "Christmas at Grandma's house 2022", ...]
}
```

## Step-by-Step Training Process

### Step 1: Convert Your Data to TSV Format

The training script expects TSV (tab-separated values) format:
```
query[TAB]positive_caption[TAB]negative1[TAB]negative2[TAB]...
```

Run the data converter:
```powershell
python finetune/data_converter.py --input data/queries.json --output_dir data/processed
```

**Options:**
- `--dev_ratio 0.02`: Use 2% of data for validation (default)
- `--samples_per_query 1`: Generate 1 training sample per query variant
- `--seed 42`: Random seed for reproducibility
- `--no_shuffle`: Don't shuffle before splitting (keeps order)

**Expected Output:**
```
✓ Loaded X memory records
✓ Total query variations: Y
✓ Generated Z training samples
✓ Train: A samples
✓ Dev: B samples
```

This creates:
- `data/processed/train.tsv` - Training data
- `data/processed/dev.tsv` - Validation data

### Step 2: Review Your Configuration

Your training configuration is in `finetune/config_memories.yaml`:

**Key Settings (Already Configured):**
- `train_tsv: data/processed/train.tsv` - Your training data
- `dev_tsv: data/processed/dev.tsv` - Your validation data
- `output_dir: runs/memories_retriever` - Where checkpoints are saved
- `epochs: 20` - Number of training passes
- `batch_size: 256` - Batch size (adjust if GPU memory issues)
- `max_len: 512` - Maximum sequence length
- `late_interaction: true` - ColBERT-style multi-vector representation
- `topk_q: 4` - Keep top 4 query token vectors
- `topk_d: 1` - Keep top 1 document token vector (fast retrieval)

**Model Architecture:**
- `d_lex_emb: 512` - Embedding dimension
- `d_lex: 192` - Lexical representation dimension
- `rank: 256` - Low-rank projection dimension
- `heads: 8` - Number of attention heads

**Training Hyperparameters:**
- `lr: 0.0002` - Learning rate
- `warmup_steps: 1500` - Warmup steps
- `ema: 0.999` - Exponential moving average for model weights
- `accum_steps: 8` - Gradient accumulation (effective batch = 256 × 8 = 2048)

**Loss Weights:**
- `lambda_ret: 1.0` - Retrieval contrastive loss
- `lambda_lex: 0.25` - Lexical matching loss
- `lambda_ent: 0.0015` - Entropy regularization
- `lambda_ortho: 0.001` - Orthogonality regularization

### Step 3: Activate Your Environment

```powershell
conda activate vertexai
```

### Step 4: Install Dependencies (if needed)

```powershell
pip install torch transformers sentence-transformers pyyaml tqdm faiss-cpu
pip install wandb  # Optional: for experiment tracking
```

### Step 5: Start Training

**Option A: Using the runner script (Recommended):**
```powershell
python finetune/run_longmatrix.py --config finetune/config_memories.yaml
```

**Option B: Direct training script:**
```powershell
python finetune/train_longmatrix.py --config finetune/config_memories.yaml
```

**With Weights & Biases tracking:**
```powershell
# Login first (one-time)
wandb login

# Then train
python finetune/run_longmatrix.py --config finetune/config_memories.yaml
```

**To disable W&B:**
Edit `config_memories.yaml` and change:
```yaml
wandb: false
```

### Step 6: Monitor Training

The training will output:
- **Loss metrics**: Total loss, retrieval loss, lexical loss, etc.
- **Dev evaluation**: Recall@10 on validation set every 0.2 epochs
- **Checkpoints**: Saved to `runs/memories_retriever/`

Example output:
```
[epoch 1] loss=0.523 | recall@10=0.456
[epoch 2] loss=0.312 | recall@10=0.678
...
```

### Step 7: Model Export (Automatic)

After training completes, the model automatically exports:
- **Model checkpoint**: `runs/memories_retriever/best_model.pt`
- **FAISS index**: `models/memories_retriever/index.faiss` (if export_after_train: true)
- **Tokenizer**: `models/memories_retriever/tokenizer/`
- **Configuration**: `runs/memories_retriever/config_used.yaml`

## Advanced Options

### Resume from Checkpoint
```yaml
resume: runs/memories_retriever/checkpoint_epoch_10.pt
```

### Adjust Batch Size (if GPU memory issues)
```yaml
batch_size: 128  # Reduce if OOM errors
accum_steps: 16  # Increase to maintain effective batch size
```

### Early Stopping
```yaml
early_stop_patience: 3  # Stop if no improvement for 3 evaluations
early_stop_min_delta: 0.0001  # Minimum improvement threshold
```

### Export Only (Skip Training)
```yaml
epochs: 0
export_after_train: true
resume: runs/memories_retriever/best_model.pt
```

## Troubleshooting

### Out of Memory (OOM)
- Reduce `batch_size` (try 128, 64, 32)
- Reduce `max_len` (try 256, 128)
- Enable gradient checkpointing: `grad_ckpt: true` (already enabled)

### Slow Training
- Increase `batch_size` if GPU allows
- Reduce `num_workers` to 0 if CPU-bound
- Disable `wandb` if network is slow

### Poor Results
- Increase `epochs` (try 30-50)
- Adjust learning rate `lr` (try 1e-4 or 3e-4)
- Increase `samples_per_query` when converting data
- Add more training data

### Missing Dependencies
```powershell
pip install -r finetune/requirements.txt  # If available
# Or manually:
pip install torch transformers sentence-transformers pyyaml tqdm faiss-cpu wandb
```

## Configuration Files Reference

1. **config_memories.yaml** - Your custom memories training config (use this!)
2. **config_used.yaml** - Original config (reference only)
3. **data_converter.py** - JSON to TSV converter
4. **train_longmatrix.py** - Main training script
5. **run_longmatrix.py** - Config-based launcher

## Questions?

- Check `runs/memories_retriever/config_used.yaml` for the exact config used
- Monitor `runs/memories_retriever/*.log` for detailed logs
- Review validation metrics to ensure model is learning

Good luck with your training! 🚀
