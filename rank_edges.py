import json, networkx as nx
from collections import defaultdict

SRC = "berkeley_edge_list_aug.json"

def build_graph(edges):
    G = nx.DiGraph()
    for e in edges:
        u, v = int(e["source"]), int(e["target"])
        w = float(e["weight"])
        bidir = bool(e.get("bidirectional", True))
        attrs = {
            "weight": w,
            "original_weight": float(e.get("original_weight", w)),
            "edge_id": int(e.get("edge_id", -1))
        }
        G.add_edge(u, v, **attrs)
        if bidir:
            G.add_edge(v, u, **attrs)
    return G

edges = json.load(open(SRC, "r", encoding="utf-8"))
G = build_graph(edges)

# Edge betweenness on directed graph; for performance you can pass k=<sample of nodes>
eb = nx.edge_betweenness_centrality(G, k=None, normalized=True, weight="weight")  # may take a bit but OK for ~4.7k edges

# Rank by score (descending)
ranked = sorted(eb.items(), key=lambda x: x[1], reverse=True)
print("Top 20 edges by betweenness (u->v, score):")
for i, ((u,v), score) in enumerate(ranked[:20], 1):
    print(f"{i:2d}. {u} -> {v} : {score:.6f}")
