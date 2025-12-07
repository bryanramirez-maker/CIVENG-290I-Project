import json, csv, networkx as nx
from copy import deepcopy

SRC = "berkeley_edge_list_aug.json"
OD = [(0,100), (10,250), (50,900), (150,850), (200,1100)]  # replace with your curated OD set

def build_graph(edges):
    G = nx.DiGraph()
    for e in edges:
        u, v = int(e["source"]), int(e["target"])
        w = float(e["weight"])
        bidir = bool(e.get("bidirectional", True))
        attrs = {
            "weight": w,
            "original_weight": float(e.get("original_weight", w)),
            "status": e.get("status", "open"),
            "direction": e.get("direction", "normal"),
            "edge_id": int(e.get("edge_id", -1)),
        }
        G.add_edge(u, v, **attrs)
        if bidir:
            G.add_edge(v, u, **attrs)
    return G

def sp_len(G, s, t):
    try:
        return nx.shortest_path_length(G, s, t, weight="weight")
    except nx.NetworkXNoPath:
        return float("inf")

def close_edge(G, u, v, both=True):
    if G.has_edge(u, v):
        G[u][v]["weight"] = float("inf"); G[u][v]["status"] = "closed"
    if both and G.has_edge(v, u):
        G[v][u]["weight"] = float("inf"); G[v][u]["status"] = "closed"

def open_edge(G, u, v, both=True):
    if G.has_edge(u, v):
        G[u][v]["weight"] = G[u][v].get("original_weight", G[u][v]["weight"])
        G[u][v]["status"] = "open"
    if both and G.has_edge(v, u):
        G[v][u]["weight"] = G[v][u].get("original_weight", G[v][u]["weight"])
        G[v][u]["status"] = "open"

def reverse_edge(G, u, v):
    if not G.has_edge(u, v):
        return False
    data = dict(G[u][v])
    G.remove_edge(u, v)
    if not G.has_edge(v, u):
        G.add_edge(v, u, **data)
    G[v][u]["weight"] = data.get("original_weight", data.get("weight", 1.0))
    G[v][u]["status"] = "open"
    G[v][u]["direction"] = "reversed"
    return True

# 1) Load edges and build graph
edges = json.load(open(SRC, "r", encoding="utf-8"))
G0 = build_graph(edges)

# 2) Baseline matrix
baseline = {(s,t): sp_len(G0, s, t) for (s,t) in OD}

# 3) Choose candidate edges (manually or from rank_edges.py output)
candidates = [(0,8), (8,11), (11,861), (67,100)]  # replace with ranked/arterial edges

with open("week2_scenarios.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["scenario","u","v","od_pairs","mean_delta_m","max_delta_m","num_disconnected"])
    for (u,v) in candidates:
        # Closure scenario
        G = deepcopy(G0)
        close_edge(G, u, v, both=True)
        deltas = []
        disc = 0
        for (s,t) in OD:
            d = sp_len(G, s, t)
            b = baseline[(s,t)]
            if b == float("inf"):
                continue
            if d == float("inf"):
                disc += 1
                delta = float("inf")
            else:
                delta = d - b
            deltas.append(delta)
        finite = [x for x in deltas if x != float("inf")]
        mean_delta = sum(finite)/len(finite) if finite else float("inf")
        max_delta = max(finite) if finite else float("inf")
        w.writerow(["closure", u, v, len(OD), f"{mean_delta:.3f}", f"{max_delta:.3f}", disc])

        # Reversal scenario
        G = deepcopy(G0)
        reverse_edge(G, u, v)
        deltas = []; disc = 0
        for (s,t) in OD:
            d = sp_len(G, s, t); b = baseline[(s,t)]
            if b == float("inf"):
                continue
            if d == float("inf"):
                disc += 1; delta = float("inf")
            else:
                delta = d - b
            deltas.append(delta)
        finite = [x for x in deltas if x != float("inf")]
        mean_delta = sum(finite)/len(finite) if finite else float("inf")
        max_delta = max(finite) if finite else float("inf")
        w.writerow(["reversal", u, v, len(OD), f"{mean_delta:.3f}", f"{max_delta:.3f}", disc])
