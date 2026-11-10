import networkx as nx
from xml_to_graph import parse_drawio_xml, merge_attributes_into_dictionary
from vectoriser import convert_to_vector, compute_similarity
import os
import re
from itertools import combinations

base_path = "data/submissions"
threshold = 0.95
passed = []

# 1. Filter for only the latest attempt of each user's submissions
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
print(f"Processing {len(target_files)} unique final submissions...")

# 2. Precompute and store all characteristic vectors in a dictionary
vectors = {}
for file in target_files:
    nodes, edges = parse_drawio_xml(os.path.join(base_path, file))
    nodes, edges = merge_attributes_into_dictionary(nodes, edges)

    G = nx.DiGraph()
    for node_id, data in nodes.items():
        G.add_node(node_id, **data)
    
    G.add_edges_from(edges)
    vectors[file] = convert_to_vector(G)

# 3. Perform exhaustive pairwise comparison
# combinations() ensures we don't compare a file to itself, and prevents duplicate pairs (e.g., A-B and B-A)
for file1, file2 in combinations(target_files, 2):
    similarity_score = compute_similarity(vectors[file1], vectors[file2])

    if similarity_score > threshold:
        passed.append((file1, file2, similarity_score))

# 4. Sort results by highest similarity score and print
passed = sorted(passed, key=lambda x: x[2], reverse=True)
for diagram in passed:
    print(f"{diagram[0]} & {diagram[1]}: {diagram[2]:.2%}")