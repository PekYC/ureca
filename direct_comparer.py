import networkx as nx
from xml_to_graph import parse_drawio_xml, merge_attributes_into_dictionary
from vectoriser import convert_to_vector, compute_similarity
import os

base_path = "data/submissions"
original_file = "102-3-48.xml"
compare_file = "114-1-48.xml"

def make_graph(xml_file):
    nodes, edges = parse_drawio_xml(xml_file)
    nodes, edges = merge_attributes_into_dictionary(nodes, edges)

    G = nx.DiGraph()
    for node_id, data in nodes.items():
        G.add_node(node_id, **data)

    # For troubleshooting
    for u, v, attr in edges:
        if u not in nodes:
            print(f"Ghost Node Found! ID {u} is in an edge but missing from nodes.")
        if v not in nodes:
            print(f"Ghost Node Found! ID {v} is in an edge but missing from nodes.")

    G.add_edges_from(edges)

    return G

original_graph = make_graph(os.path.join(base_path, original_file))
compare_graph = make_graph(os.path.join(base_path, compare_file))

original_vector = convert_to_vector(original_graph)
compare_vector = convert_to_vector(compare_graph)

k1 = original_vector.keys()
print(original_vector)
exit()
k2 = compare_vector.keys()
print("Keys in both:")
print(k1&k2)

print("\nKeys in original but not compare:")
print(k1-k2)

print("\nKeys in compare but not original:")
print(k2-k1)

print(f"Similarity score: {compute_similarity(original_vector, compare_vector):.2f}")