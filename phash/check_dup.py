import os
import json
from PIL import Image
from utils import *

image_path = "data/plagiarised/7178/71-4-48.png"
img = Image.open(image_path)

index_path = "phash/faiss_index"
index = load_index(index_path)

with open("phash/index_metadata.json", "r") as f:
    image_filenames = json.load(f)

img_hash = hash_image(img)
D, I = check_duplicate(index, img_hash, 100)

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
else:
    print("No dups found")