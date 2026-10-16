import networkx as nx
import matplotlib.pyplot as plt
from xml_to_graph import parse_drawio_xml

nodes, edges = parse_drawio_xml("data/data.xml")
print(f"Extracted {len(nodes)} nodes and {len(edges)} connections.")

# count = 0
# for id, details in nodes.items():
#     if details["type"] == "Entity":
#         print(f"{id}: {details["label"]}")
#         count += 1
# print(count)

# for edge in edges:
#     source = edge[0]
#     target = edge[1]

    # print(f"[{nodes[source]["label"]} -> {nodes[target]['label']}]")

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

nx.draw_spring(G, with_labels=True)
plt.show()