import torch 
import timm
from PIL import Image
import numpy as np
import faiss
from faiss import IndexFlatIP

model = timm.create_model('hf-hub:timm/vit_base_patch16_radio_v3.c_radio', pretrained=True).eval()
data_config = timm.data.resolve_model_data_config(model)
transforms = timm.data.create_transform(**data_config, is_training=False)

def extract_features(im: Image) -> np.ndarray:
    im = im.convert("RGB")
    x = transforms(im).unsqueeze(0)

    with torch.inference_mode():
        tokens = model.forward_features(x)

    summary = tokens[:, [0, 1, 2]].flatten(1)

    return summary.numpy().astype('float32')

def load_index(filename: str = "faiss_index") -> IndexFlatIP:
    try:
        return faiss.read_index(f"{filename}")
    except RuntimeError:
        return IndexFlatIP(2304)

def save_index(index: IndexFlatIP, filename: str = "faiss_index") -> None:
    faiss.write_index(index, filename)

def check_duplicate(index: IndexFlatIP, img_hash: np.ndarray, thresh: float) -> tuple[np.ndarray, np.ndarray]:
    (lims, D, I) = index.range_search(img_hash, thresh)
    return (D, I)