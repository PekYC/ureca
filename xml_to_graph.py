import xml.etree.ElementTree as ET
import math
import re

def parse_drawio_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    nodes = {}
    edges = []
    referential_constraints = {}

    def clean_text(raw_val):
        """
            Recursively removes HTML tags like <div>, <font>
        """
        if not raw_val:
            return ""

        text = re.sub(r'<[^>]+>', '', raw_val)
        return text.replace('&gt;', '>').replace('&lt;', '<').strip()

    def get_shape_type(style):
        if "shape=rhombus" in style:
            return "Relationship"
        elif "ellipse" in style:
            return "Attribute"
        elif "shape=mxgraph.basic.arc" in style:
            return "Referential Constraint"
        elif "triangle" in style:
            return "Subclass"
        elif "text" in style:
            return "Text"
        elif "whiteSpace=wrap" in style or "rounded=0" in style:
            return "Entity"
        return "Unknown"

    def findIntended(nodes, point_x, point_y, threshold=15.0):
        closest_node = None
        min_dist = float("inf")

        for node_id, node_data in nodes.items():
            nodex, nodey, nodew, nodeh = node_data['bbox']
            node_left, node_right = nodex, nodex + nodew
            node_top, node_bottom = nodey, nodey + nodeh

            # Calculate distance from the exact arc tip to the entity's bounding box
            dx = max(0, node_left - point_x, point_x - node_right)
            dy = max(0, node_top - point_y, point_y - node_bottom)

            dist = math.hypot(dx, dy)

            if dist < min_dist:
                min_dist = dist
                closest_node = node_id


#         print(f"Mid angle: {mid_angle} (0-1)\n\
# rotation: {orientation}\n\
# direction: {direction}\n\
# offset_angle: {mid_angle_offsetted}\n\
# tip_x: {tip_x}\n\
# tip_y: {tip_y}\n\
# original_xy = ({cx}, {cy})")

        # Using 15px threshold to account for Draw.io's visual gaps between arrows and shapes
        if min_dist <= 15.0:
            return closest_node

        return None


    def findIntendedNode(nodes, arc_obj):
        ax, ay, aw, ah = arc_obj["bbox"]
        cx = ax + (aw / 2.0)
        cy = ay + (ah / 2.0)

        start_angle = arc_obj["start_angle"]
        end_angle = arc_obj["end_angle"]
        orientation = arc_obj["orientation"]
        direction = arc_obj["direction"]

        length = (end_angle - start_angle) % 1.0
        mid_angle = (start_angle + (length/2.0)) % 1.0

        # Applying offset
        if direction == "south":
            offset = 0.25
        elif direction == "west":
            offset = 0.5
        elif direction == "north":
            offset = 0.75
        else:
            offset = 0

        mid_angle_offsetted = (mid_angle + offset) % 1.0

        # Converting to degrees
        mid_angle_deg = ((mid_angle_offsetted - 0.25) % 1.0) * 360

        final_angle_deg = (mid_angle_deg + orientation) % 360
        theta_rad = math.radians(final_angle_deg)

        tip_x = cx + (aw / 2.0) * math.cos(theta_rad)
        tip_y = cy + (ah / 2.0) * math.sin(theta_rad)

        return findIntended(nodes, tip_x, tip_y)

    for cell in root.findall(".//mxCell[@vertex='1']"):
        cell_id = cell.get("id")

        if cell_id in ("0", "1"):
            continue # Skipping root layers

        # Getting nodes
        geom = cell.find("mxGeometry")
        if geom is not None:
            x = float(geom.get("x", 0.0))
            y = float(geom.get("y", 0.0))
            w = float(geom.get('width', 0.0))
            h = float(geom.get('height', 0.0))

            # For reconnecting edges later
            node_type = get_shape_type(cell.get("style", ""))
            if node_type == "Referential Constraint":
                style_string = cell.get("style")
                orientation = re.search(r'rotation=(-?\d+\.?\d*)', style_string)
                start_match = re.search(r'startAngle=(-?\d+\.?\d*)', style_string)
                end_match = re.search(r'endAngle=(-?\d+\.?\d*)', style_string)
                direction_match = re.search(r'direction=([a-zA-Z]+)', style_string)

                referential_constraints[cell_id] = {
                    "bbox": (x, y, w, h),
                    "orientation": float(orientation.group(1)) if orientation else 0.0,
                    "start_angle": float(start_match.group(1)) if start_match else 0.0,
                    "end_angle": float(end_match.group(1)) if end_match else 0.0,
                    "direction": direction_match.group(1).lower() if direction_match else 'east'
                }
            else:
                nodes[cell_id] = {
                    "label": clean_text(cell.get("value", "")),
                    "type": node_type,
                    "centroid": (x+w/2.0, y+h/2.0),
                    "bbox": (x, y, w, h) 
                    # bbox is only for identifying arcs, probably 
                    # not used for analysis 
                }

    print(f"All {len(nodes)} nodes and {len(referential_constraints)} ref cons added!")
    for cell in root.findall(".//mxCell[@edge='1']"):
        src = cell.get("source")
        tgt = cell.get("target")
        cardinality = "m"

        if src is None:
            src_point_tag = cell.find("./mxGeometry/mxPoint[@as='sourcePoint']")

            if src_point_tag is not None:
                src_x = float(src_point_tag.get("x", 0.0))
                src_y = float(src_point_tag.get("y", 0.0))

                src = findIntended(nodes, src_x, src_y)
                # print(f"Fixed a src! New source is {nodes[src]["label"]}. It has {nodes[src]["centroid"]}")

        if tgt is None:
            tgt_point_tag = cell.find("./mxGeometry/mxPoint[@as='targetPoint']")

            if tgt_point_tag is not None:
                tgt_x = float(tgt_point_tag.get("x", 0.0))
                tgt_y = float(tgt_point_tag.get("y", 0.0))

                tgt = findIntended(nodes, tgt_x, tgt_y)
                # print(f"Fixed a tgt! New target is {nodes[tgt]["label"]}. It has {nodes[tgt]["centroid"]}")

        if src in referential_constraints:
            # print(f"Problem with ref con {src}. Looking for nearest node...")
            node_id = findIntendedNode(nodes, referential_constraints[src])
            # print(f"Found intended node for {src}, it is {nodes[node_id]['label']}")
            src = node_id
            cardinality = "1"
        elif tgt in referential_constraints:
            # print(f"Problem with ref con {tgt}. Looking for nearest node...")
            node_id = findIntendedNode(nodes, referential_constraints[tgt])
            # print(f"Found intended node for {tgt}, it is {nodes[node_id]['label']}")
            tgt = node_id
            cardinality = "1"

        if src and tgt:
            if src in nodes and tgt in nodes:
                edges.append((src, tgt, {"cardinality":cardinality}))
            else:
                print(f"Edge with missing src or tgt found. Details: src={src}, tgt={tgt}")

    return nodes, edges


def merge_attributes_into_dictionary(nodes, edges):
    nodes_copy = nodes.copy()

    for node_id, node_data in nodes_copy.items():
        if node_data.get("type") == "Attribute":
            connected_edges = [edge for edge in edges if edge[0] == node_id or edge[1] == node_id]

            if connected_edges:
                connected_edge = connected_edges[0]
                target_node_id = connected_edge[0] if connected_edge[1] == node_id else connected_edge[1]

                if target_node_id in nodes:
                    if "attributes" not in nodes[target_node_id]:
                        nodes[target_node_id]["attributes"] = []

                    edges = [edge for edge in edges if edge not in connected_edges]

            del nodes[node_id]

    return nodes, edges
