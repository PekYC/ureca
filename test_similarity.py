import networkx as nx
from xml_to_graph import parse_drawio_xml, merge_attributes_into_dictionary
from vectoriser import convert_to_vector, compute_similarity
import os

base_path = "data/submissions"
target_file = "102-1-48.xml"

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


for file in os.listdir(base_path):
    if file == target_file:
        continue
    print(f"======= Processing {file} ==========")
    
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
    print(compare_vector.keys())

    print(f"Similarity score: {compute_similarity(target_vector, compare_vector)}")