"""
    phash creates a hash for each image and stores them in an IndexBinaryFloat.
    It is a physical file which represents the entire dataset compressed.
    Meaning, each time we add a new file to the dataset, we need to hash it and
    add to the IndexBinaryFloat file.
"""


from io import BytesIO
import faiss
import numpy as np
from imagehash import dhash
from PIL import Image
from faiss import IndexBinaryFlat

def read_imagefile(data) -> Image.Image:
    image = Image.open(BytesIO(data))
    return image

def hash_image(im: Image, hash_size: int = 16) -> np.ndarray:
    im_hash = dhash(im, hash_size=hash_size)

    return np.packbits(np.array(im_hash.hash).reshape(1, hash_size**2), axis=1)


def load_index(filename: str = "faiss_index", hash_size: int = 16) -> IndexBinaryFlat:
    """
        Returns an IndexBinaryFlat object from a file, or create a new one if doesn't exist
    """
    d = hash_size **2
    try:
        return faiss.read_index_binary(f"{filename}_{d}")
    except RuntimeError:
        return IndexBinaryFlat(d)

def save_index(index: IndexBinaryFlat, filename: str = "faiss_index", hash_size: int = 16) -> None:
    """
        Save an IndexBinaryFlat object to a given filename.
    """
    d = hash_size **2
    faiss.write_index_binary(index, f"{filename}_{d}")

def check_duplicate(index: IndexBinaryFlat, img_hash: np.ndarray, thresh: int) -> tuple[np.ndarray, np.ndarray]:
    """
        D is an array of Hamming distances: [0, 3] (lower means more match)
        I is an array of matching image's ID in the index file: [42, 105]

        Will only return image IDs which are less than threshold.
    """
    (lims, D, I) = index.range_search(img_hash, thresh)
    return (D, I)