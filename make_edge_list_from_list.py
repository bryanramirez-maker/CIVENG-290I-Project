import json
from pathlib import Path

SRC = Path("berkeley_graph_list.json")     # list-of-lists format we created earlier
DST = Path("berkeley_edge_list.json")      # edge-list JSON for your API

L = json.loads(SRC.read_text(encoding="utf-8"))

edges = []
seen = set()  # to avoid duplicates (i<j)
for i, nbrs in enumerate(L):
    for j, w in nbrs:
        a, b = sorted((int(i), int(j)))
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        edges.append({
            "source": str(a),
            "target": str(b),
            "weight": float(w),
            "bidirectional": True
        })

DST.write_text(json.dumps(edges, indent=2), encoding="utf-8")
print(f"wrote {DST} with {len(edges)} edges")
