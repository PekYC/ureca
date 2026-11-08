"""
    Get the graphical representation of each file in the submissions folder. 
    Also plots it.
"""


import os
import networkx as nx
import matplotlib.pyplot as plt
from xml_to_graph import parse_drawio_xml, merge_attributes_into_dictionary


INPUT_PATH = "data/submissions"

for file in os.listdir(INPUT_PATH):
    if file != "26-3-48.xml":
        continue
    nodes, edges = parse_drawio_xml(os.path.join(INPUT_PATH, file))
    print(f"Extracted {len(nodes)} nodes and {len(edges)} connections.")

    print("Merging attributes...")
    nodes, edges = merge_attributes_into_dictionary(nodes, edges)

    print(nodes)
    print(edges)

    for edge in edges:
        source = edge[0]
        target = edge[1]

        print(f"[{nodes[source]['label']} -> {nodes[target]['label']}]")

    # 1. Ensure your edges list contains the EXACT string IDs used in the nodes dict
    G = nx.DiGraph()
    for node_id, data in nodes.items():
        G.add_node(node_id, **data)

    for u, v, attr in edges:
        if u not in nodes:
            print(f"Ghost Node Found! ID {u} is in an edge but missing from nodes.")
        if v not in nodes:
            print(f"Ghost Node Found! ID {v} is in an edge but missing from nodes.")

    G.add_edges_from(edges)

    # 2. Extract the exact (x, y) coordinates you calculated in Phase 1
    # for node_id, data in G.nodes(data=True):
        # print(data)

    pos = {node_id: (data["centroid"][0], data["centroid"][1]) for node_id, data in G.nodes(data=True)}

    # 3. Draw the graph using those fixed positions
    plt.figure(figsize=(12, 8))
    plt.title(file, fontsize=12, fontweight="bold")
    nx.draw(
        G, 
        pos=pos,                 # Forces nodes into their original Draw.io positions
        with_labels=True, 
        labels={node_id: data.get("label", node_id) for node_id, data in G.nodes(data=True)},
        node_color="lightblue", 
        node_size=800, 
        font_size=8,
        arrows=False,           
        edge_color="black"       # Ensure edges are visible
    )

    # Optional: Draw the edge attributes (cardinalities)
    edge_labels = {(u, v): d.get("cardinality", "") for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    # Remember to invert the Y-axis so it matches Draw.io's screen coordinates
    plt.gca().invert_yaxis()
    plt.show()