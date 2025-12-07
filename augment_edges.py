# augment_edges.py
import json

SRC = "berkeley_edge_list.json"       # existing edge list to upload to FastAPI
DST = "berkeley_edge_list_aug.json"   # new file with extra fields

edges = json.load(open(SRC, "r", encoding="utf-8"))

aug = []
for k, e in enumerate(edges):
    rec = dict(e)
    rec["edge_id"] = k                 # stable id for referencing
    rec["original_weight"] = float(e["weight"])
    rec["status"] = "open"             # open | closed
    rec["direction"] = "normal"        # normal | reversed (metadata only)
    aug.append(rec)

json.dump(aug, open(DST, "w", encoding="utf-8"), indent=2)
print(f"Augmented {len(aug)} edges -> {DST}")
