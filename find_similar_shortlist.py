"""
    For a given file in "target_file", return the similarity scores of all
    other xml comparisons above a certain threshold.
"""

import networkx as nx
from xml_to_graph import parse_drawio_xml, merge_attributes_into_dictionary
from vectoriser import convert_to_vector, compute_similarity
import os
import re

base_path = "data/submissions"
target_file = "55-5-48.xml"
threshold = 0.85
passed = []

nodes, edges = parse_drawio_xml(os.path.join(base_path, target_file))
print(f"Extracted {len(nodes)} nodes and {len(edges)} connections.")

print("Merging attributes...")
nodes, edges = merge_attributes_into_dictionary(nodes, edges)

G1 = nx.DiGraph()
for node_id, data in nodes.items():
    G1.add_node(node_id, **data)

for u, v, attr in edges:
    if u not in nodes:
        print(f"Ghost Node Found! ID {u} is in an edge but missing from nodes.")
    if v not in nodes:
        print(f"Ghost Node Found! ID {v} is in an edge but missing from nodes.")

G1.add_edges_from(edges)

target_vector = convert_to_vector(G1)
print(target_vector.keys())


# Taking only the last attempt of each user's submissions
pattern = re.compile(r"^(\d+)-(\d+)-.*\.xml$")
latest_attempts = {}
for file in os.listdir(base_path):
    match = pattern.match(file)
    if not match:
        continue

    user_id = match.group(1)
    attempt = int(match.group(2))

    if user_id not in latest_attempts or attempt > latest_attempts[user_id][0]:
        latest_attempts[user_id] = (attempt, file)

target_files = [filename for attempt, filename in latest_attempts.values()]

for file in target_files:
    if file == target_file:
        continue
    
    nodes, edges = parse_drawio_xml(os.path.join(base_path, file))
    nodes, edges = merge_attributes_into_dictionary(nodes, edges)

    G2 = nx.DiGraph()
    for node_id, data in nodes.items():
        G2.add_node(node_id, **data)

    for u, v, attr in edges:
        if u not in nodes:
            print(f"Ghost Node Found! ID {u} is in an edge but missing from nodes.")
        if v not in nodes:
            print(f"Ghost Node Found! ID {v} is in an edge but missing from nodes.")

    G2.add_edges_from(edges)

    compare_vector = convert_to_vector(G2)
    similarity_score = compute_similarity(target_vector, compare_vector)

    if similarity_score > threshold:
        passed.append((file, similarity_score))

passed = sorted(passed, key=lambda x: x[1])[::-1]
for diagram in passed:
    print(f"{diagram[0]}: {diagram[1]:.2%}")