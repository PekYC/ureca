import os
import json
from PIL import Image
import matplotlib.pyplot as plt
from utils import *

def load_gt(filepath: str) -> set[tuple[str, str]]:
    gt = set()
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split(", ")
            gt.add(tuple(sorted(parts)))

    return gt            

def find_plagiarised(data_path: str, index_file: str, threshold: int) -> dict[str, list[str]]:
    output = {}
    index = load_index(index_file)
    images = [x for x in os.listdir(data_path) if x.endswith(".png")]
    with open("phash/index_metadata.json", "r") as f:
        image_filenames = json.load(f)

    for image in images:
        with Image.open(os.path.join(data_path, image)) as img:
            img_hash = hash_image(img)

        D, I = check_duplicate(index, img_hash, threshold)

        if len(I) > 0:
            for i in range(len(I)):
                faiss_id = I[i]
                filename = image_filenames[faiss_id]
                if filename != image:
                    output.setdefault(image, []).append(filename)

    return output

def evaluate_threshold(data_path: str, index_file: str, gt_file: str, thresholds: list[int]) -> dict:
    gt = load_gt(gt_file)
    results = {}

    print(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'TP':<4} | {'FP':<4} | {'FN':<4}")
    print("-" * 65)

    for thresh in thresholds:
        plagiarised_dict = find_plagiarised(data_path, index_file, thresh)

        predicted_pairs = set()
        for key, values in plagiarised_dict.items():
            for value in values:
                predicted_pairs.add(tuple(sorted((key, value))))

        tp = len(predicted_pairs.intersection(gt))
        fp = len(predicted_pairs - gt)
        fn = len(gt - predicted_pairs)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        results[thresh] = {
            "Precision": precision,
            "Recall": recall,
            "TP": tp,
            "FP": fp,
            "FN": fn
        }
        
        print(f"{thresh:<10} | {precision:<10.4f} | {recall:<10.4f} | {tp:<4} | {fp:<4} | {fn:<4}")

    return results


results = evaluate_threshold("data/union", "phash/faiss_index", "data/union/plagiarisms.txt", [x for x in range(60, 121, 10)])

keys = sorted(results.keys())

precision = []
recall = []
f1 = []

for k in keys:
    p = results[k]["Precision"]
    r = results[k]["Recall"]

    precision.append(p)
    recall.append(r)

    if p+r == 0:
        f1.append(0.0)
    else:
        f1.append(2 * (p  *r)/(p+r))

# Create the plot
plt.figure(figsize=(10, 6))

plt.plot(keys, precision, label='Precision', marker='o', color='#1f77b4', linewidth=2)
plt.plot(keys, recall, label='Recall', marker='s', color='#ff7f0e', linewidth=2)
plt.plot(keys, f1, label='F1 Score', marker='^', color='#2ca02c', linewidth=2)

# Formatting the chart
plt.title('Precision, Recall, and F1 Score by Parameter')
plt.xlabel('Parameter Key')
plt.ylabel('Score (0.0 to 1.0)')
plt.xticks(keys) # Ensure all keys show up on the X-axis
plt.ylim(-0.05, 1.05) # Add a little padding to the Y-axis
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Display the chart
plt.show()



print("Using '80' as threshold, identified plagiarisms:")
plagiarised = find_plagiarised("data/union", "phash/faiss_index", 80)
for k, v in plagiarised.items():
    print(f"{k:^15} <---> {v[0]:^15}")