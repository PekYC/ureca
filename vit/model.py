from urllib.request import urlopen
from PIL import Image
import torch
import timm

img = Image.open(urlopen(
    'https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/beignets-task-guide.png'
))

model = timm.create_model('hf-hub:timm/vit_base_patch16_radio_v3.c_radio', pretrained=True).eval()
data_config = timm.data.resolve_model_data_config(model)
transforms = timm.data.create_transform(**data_config, is_training=False)
x = transforms(img).unsqueeze(0)

with torch.inference_mode():
    tokens = model.forward_features(x)  # (1, 1032, 768): prefix + patch tokens
    embedding = model.forward_head(tokens, pre_logits=True)  # (1, 768): first CLS token

# RADIO style outputs
summary = tokens[:, [0, 1, 2]].flatten(1)  # (1, 2304)
spatial = tokens[:, model.num_prefix_tokens:]  # (1, 1024, 768)

print(f"Tokens shape: {tokens.shape}")       
# Expected: torch.Size([1, 1032, 768])

print(f"Embedding shape: {embedding.shape}") 
# Expected: torch.Size([1, 768])

print(f"Summary shape: {summary.shape}")     
# Expected: torch.Size([1, 2304])

print(f"Spatial shape: {spatial.shape}")     
# Expected: torch.Size([1, 1024, 768])