import os
import json
from PIL import Image
from utils import *

base_path = "data/full_data_final"
image_folder = os.listdir(base_path)
image_folder = [x for x in image_folder if x.endswith(".png")]
index_path = "phash/faiss_index"
image_filenames = []


index = load_index(index_path)
for image in image_folder:
    full_path = os.path.join(base_path, image)
    img = Image.open(full_path)
    img_hash = hash_image(img)

    index.add(img_hash)
    save_index(index, index_path)

    image_filenames.append(image)

print(f"Total images stored (ntotal): {index.ntotal}")
print(f"Hash dimension (d): {index.d}")

with open("phash/index_metadata.json", "w") as f:
    json.dump(image_filenames, f)