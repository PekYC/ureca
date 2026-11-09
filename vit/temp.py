import faiss
import os

# 1. Check if the file actually exists
filename = 'vit/faiss_index'
if not os.path.exists(filename):
    print(f"Error: The file {filename} does not exist.")
else:
    # 2. Load the index
    index = faiss.read_index(filename)
    
    # 3. Check the core properties
    print(f"Index loaded successfully!")
    print(f"Total images stored (ntotal): {index.ntotal}")
    print(f"Hash dimension (d): {index.d}")