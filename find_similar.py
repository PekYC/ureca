import networkx as nx
from xml_to_graph import parse_drawio_xml, merge_attributes_into_dictionary
from vectoriser import convert_to_vector, compute_similarity
import os
import re

base_path = "data/submissions"
target_file = "102-1-48.xml"
output_log = "output.txt"

def print_log(*args, sep=" ", end="\n", file_path=output_log):
    message = sep.join(str(arg) for arg in args) + end
    
    # 1. Print to console
    print(*args, sep=sep, end=end)
    
    # 2. Append to file
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(message)



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
    print_log(f"======= Processing {file} ==========")
    
    nodes, edges = parse_drawio_xml(os.path.join(base_path, file))
    print(f"Extracted {len(nodes)} nodes and {len(edges)} connections.")

    print("Merging attributes...")
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
    print_log(compare_vector.keys())

    print_log(f"Similarity score: {compute_similarity(target_vector, compare_vector)}")