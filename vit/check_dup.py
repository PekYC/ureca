import json
import faiss
from PIL import Image
from utils import *

image_path = "data/union/71-4-48.png"
index = load_index("vit/faiss_index")

with open("vit/index_metadata.json", "r") as f:
    image_filenames = json.load(f)

with Image.open(image_path) as img:
    img_vector = extract_features(img)
    faiss.normalize_L2(img_vector)

D, I = check_duplicate(index, img_vector, 0.8)

print(D)
print("***")
print(I)

if len(I) > 0:
    print(f"Found {len(I)} matches")

    for i in range(len(I)):
        faiss_id = I[i]
        distance = D[i]
        filename = image_filenames[faiss_id]

        print(f"Match: {filename} (Distance: {distance})")