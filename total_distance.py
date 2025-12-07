import json

# 1. Load your edge-list JSON (the one you uploaded to FastAPI)
with open("berkeley_edge_list.json", "r", encoding="utf-8") as f:
    edges = json.load(f)

# 2. Build a simple lookup:  (source,target) → weight
edge_weights = {}
for e in edges:
    s, t, w = int(e["source"]), int(e["target"]), float(e["weight"])
    edge_weights[(s, t)] = w
    if e.get("bidirectional", False):
        edge_weights[(t, s)] = w

# 3. Use the path you got from FastAPI
path = [0,8,11,861,6,249,7,2,936,27,540,539,542,943,277,
        543,544,545,930,382,383,772,55,59,98,66,101,67,100]

# 4. Compute total distance
total_distance = sum(
    edge_weights.get((path[i], path[i+1]), 0)
    for i in range(len(path)-1)
)

print(f"Total distance: {total_distance:.3f} meters ({total_distance/1000:.3f} km)")
