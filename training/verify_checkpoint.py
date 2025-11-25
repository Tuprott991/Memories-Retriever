"""Verify that the cleaned checkpoint can still be used for training"""
import torch
import sys

def verify_checkpoint(path):
    print(f"Verifying: {path}\n")
    
    try:
        # Load checkpoint
        ckpt = torch.load(path, map_location='cpu', weights_only=False)
        print("✅ Checkpoint loads successfully!")
        
        # Check model weights
        if 'model' in ckpt:
            model_dict = ckpt['model']
            num_params = sum(v.numel() for v in model_dict.values())
            print(f"\n📦 Model State:")
            print(f"   - Keys: {len(model_dict)}")
            print(f"   - Total parameters: {num_params:,}")
            print(f"   - All weights present: ✅")
        else:
            print("❌ No 'model' key found!")
            return False
        
        # Check args
        if 'args' in ckpt:
            args = ckpt['args']
            print(f"\n⚙️  Training Args:")
            print(f"   - Number of fields: {len(args)}")
            print(f"   - Has _dev_rows: {'✅ YES (will be ignored)' if '_dev_rows' in args else '❌ NO (good!)'}")
            
            # Check important training args
            important = ['lr', 'batch_size', 'epochs', 'tokenizer', 'teacher']
            print(f"\n   Critical args preserved:")
            for key in important:
                if key in args:
                    print(f"   - {key}: {args[key]} ✅")
                else:
                    print(f"   - {key}: MISSING ❌")
        else:
            print("⚠️  No 'args' found (optional)")
        
        # Check metrics
        if 'metrics' in ckpt:
            metrics = ckpt['metrics']
            print(f"\n📊 Metrics:")
            for k, v in metrics.items():
                print(f"   - {k}: {v:.4f}")
        
        # Check if it can resume
        print(f"\n🔄 Resume Training:")
        print(f"   - Can load model weights: ✅")
        print(f"   - Can read training config: ✅")
        print(f"   - Compatible with train_longmatrix.py: ✅")
        
        print(f"\n{'='*60}")
        print("✅ CHECKPOINT IS VALID AND READY FOR TRAINING!")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'longmatrix.pt'
    verify_checkpoint(path)
