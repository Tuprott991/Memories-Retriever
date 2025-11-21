import torch

ckpt_path = r"C:\Users\Vatuk\OneDrive - VNU-HCMUS\Documents\eva02_S_pt_in21k_p14.pt"

# Load checkpoint
ckpt = torch.load(ckpt_path, map_location="cpu")

# Lấy state_dict
if "state_dict" in ckpt:
    state_dict = ckpt["state_dict"]
elif "model" in ckpt:
    state_dict = ckpt["model"]
else:
    state_dict = ckpt  # file lưu trực tiếp state_dict

# Tính số tham số
total_params = sum(p.numel() for p in state_dict.values())

print(f"Total parameters: {total_params:,}")
print(f"Total parameters (millions): {total_params/1e6:.2f}M")