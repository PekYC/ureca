from collections import Counter
import numpy as np

def convert_to_vector(graph):
    counts = Counter()
    for node, data in graph.nodes(data=True):
        ntype = data.get("type", "unknown")
        in_d, out_d = graph.in_degree(node), graph.out_degree(node)
        counts[f"node_{ntype}_{in_d}_{out_d}"] += 1

    for u, v in graph.edges():
        t_u, t_v = graph.nodes[u].get("type"), graph.nodes[v].get("type")
        counts[f"path_{t_u}_{t_v}"] += 1

    return counts

def compute_similarity(c1, c2):
    all_keys = set(c1.keys()).union(c2.keys())
    v1 = np.array([c1.get(k, 0) for k in all_keys], dtype=float)
    v2 = np.array([c2.get(k, 0) for k in all_keys], dtype=float)
    norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)

    return np.dot(v1, v2) / (norm1 * norm2) if norm1 and norm2 else 0.0