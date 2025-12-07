import os
import json
import networkx as nx
import osmnx as ox
from shapely.geometry import LineString, Point, MultiLineString

# 1) Load your OSM XML file
osm_path = "map.osm"
print(f"Loading OSM from: {os.path.abspath(osm_path)}")

G = ox.graph_from_xml(osm_path, bidirectional=True, simplify=True)

print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))

# 2) Convert all geometry objects (LineString, MultiLineString) to plain lists
for _, _, data in G.edges(data=True):
    geom = data.get("geometry")
    if isinstance(geom, LineString):
        data["geometry"] = list(geom.coords)
    elif isinstance(geom, MultiLineString):
        # flatten multilinestrings
        data["geometry"] = [list(line.coords) for line in geom.geoms]

for _, data in G.nodes(data=True):
    geom = data.get("geometry")
    if isinstance(geom, Point):
        data["geometry"] = list(geom.coords)[0]

# 3) Convert to JSON-safe structure
data = nx.node_link_data(G)

out_path = "berkeley_graph.json"
with open(out_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"Graph exported successfully to: {os.path.abspath(out_path)}")
print("Sample node IDs:", list(G.nodes)[:5])
