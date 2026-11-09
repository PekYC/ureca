import os
import json
from PIL import Image
from utils import * 

base_path = "data/union"
image_folder = os.listdir(base_path)
image_folder = [x for x in image_folder if x.endswith(".png")]
index_path = "vit/faiss_index"
image_filenames = []

index = load_index(index_path)
for image in image_folder:
    full_path = os.path.join(base_path, image)
    with Image.open(full_path) as img:
        img_vector = extract_features(img)
        faiss.normalize_L2(img_vector)

        index.add(img_vector)
        image_filenames.append(image)


save_index(index, index_path)

print(f"Total images stored (ntotal): {index.ntotal}")
print(f"Hash dimension (d): {index.d}")

with open("vit/index_metadata.json", "w") as f:
    json.dump(image_filenames, f)