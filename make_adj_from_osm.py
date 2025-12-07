import json
from pathlib import Path
import osmnx as ox

OSM = Path("map.osm")                    # your exported OSM file
OUT = Path("berkeley_graph_adj.json")    # adjacency JSON your API expects

print("Loading OSM from:", OSM.resolve())
G = ox.graph_from_xml(OSM, bidirectional=True, simplify=True)

print("Nodes:", len(G.nodes), "Edges:", len(G.edges))

# Build undirected adjacency with 'length' if present, else 1
adj = {}
for u, v, data in G.edges(data=True):
    w = data.get("length", 1)
    su, sv = str(u), str(v)
    adj.setdefault(su, {})[sv] = w
    adj.setdefault(sv, {})[su] = w

with OUT.open("w", encoding="utf-8") as f:
    json.dump(adj, f, indent=2)

print("Wrote", OUT.resolve(), "with", len(adj), "nodes")
