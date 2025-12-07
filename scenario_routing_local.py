# scenario_routing_local.py
import json
import networkx as nx
from typing import List, Tuple

SRC = "berkeley_edge_list_aug.json"

def build_graph_from_edges(edges):
    """Build a DiGraph and store original weights for restoration."""
    G = nx.DiGraph()
    for e in edges:
        s = int(e["source"])
        t = int(e["target"])
        w = float(e["weight"])
        bidir = bool(e.get("bidirectional", True))

        # forward edge
        G.add_edge(s, t,
                   weight=w,
                   original_weight=float(e.get("original_weight", w)),
                   status=e.get("status", "open"),
                   direction=e.get("direction", "normal"),
                   edge_id=int(e["edge_id"]))

        # reverse if bidirectional
        if bidir:
            G.add_edge(t, s,
                       weight=w,
                       original_weight=float(e.get("original_weight", w)),
                       status=e.get("status", "open"),
                       direction=e.get("direction", "normal"),
                       edge_id=int(e["edge_id"]))  # same edge_id tags the pair
    return G

def shortest_path_info(G, start: int, end: int):
    path = nx.shortest_path(G, start, end, weight="weight")
    dist = nx.shortest_path_length(G, start, end, weight="weight")
    return path, dist

def edges_on_path(G, path: List[int]) -> List[Tuple[int,int]]:
    return [(path[i], path[i+1]) for i in range(len(path)-1)]

def close_edge(G, u: int, v: int, both=True):
    """Block an edge by setting weight = inf and status=closed."""
    if G.has_edge(u, v):
        G[u][v]["weight"] = float("inf")
        G[u][v]["status"] = "closed"
    if both and G.has_edge(v, u):
        G[v][u]["weight"] = float("inf")
        G[v][u]["status"] = "closed"

def open_edge(G, u: int, v: int, both=True):
    """Restore an edge to its original weight and status=open."""
    if G.has_edge(u, v):
        G[u][v]["weight"] = G[u][v]["original_weight"]
        G[u][v]["status"] = "open"
    if both and G.has_edge(v, u):
        G[v][u]["weight"] = G[v][u]["original_weight"]
        G[v][u]["status"] = "open"

def reverse_edge(G, u: int, v: int):
    """
    Simulate a contraflow flip for a directed pair:
    remove u->v, ensure v->u exists with the original_weight, mark metadata.
    For bidirectional corridors, call this on every pair segment you want reversed.
    """
    if not G.has_edge(u, v):
        return False
    data = dict(G[u][v])
    # Remove u->v
    G.remove_edge(u, v)
    # Ensure v->u exists with original weight
    if not G.has_edge(v, u):
        G.add_edge(v, u, **data)
    # Update v->u attributes to reflect "reversed"
    G[v][u]["weight"] = data.get("original_weight", data.get("weight", 1.0))
    G[v][u]["status"] = "open"
    G[v][u]["direction"] = "reversed"
    return True

if __name__ == "__main__":
    edges = json.load(open(SRC, "r", encoding="utf-8"))
    G = build_graph_from_edges(edges)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} directed edges")

    # 1) Baseline
    s, t = 0, 100
    path0, d0 = shortest_path_info(G, s, t)
    print("Baseline:", d0, "m")
    # 2) Block one edge along the baseline path and re-solve
    u,v = edges_on_path(G, path0)[2]   # pick the 3rd segment as an example
    close_edge(G, u, v, both=True)
    path1, d1 = shortest_path_info(G, s, t)
    print("After closure:", d1, "m")
    # 3) Restore and test a contraflow reversal on the same segment
    open_edge(G, u, v, both=True)
    reverse_edge(G, u, v)
    path2, d2 = shortest_path_info(G, s, t)
    print("After reversal:", d2, "m")
