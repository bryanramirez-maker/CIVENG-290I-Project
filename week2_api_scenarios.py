import requests, csv, math

BASE = "https://two90i-assignment3-kfbu.onrender.com"

OD   = [(0,100),(8,67),(11,861),(67,100),(50,900)]
CAND = [(0,8),(8,11),(11,861),(67,100)]

def sp(s,t):
    r = requests.get(
        f"{BASE}/solve_shortest_path/start_node_id={s}&end_node_id={t}",
        timeout=30,
    ).json()
    d = r.get("total_distance")
    # Treat None/NaN/Inf as disconnected
    if d is None:
        return None
    try:
        d = float(d)
    except Exception:
        return None
    return d if math.isfinite(d) else None

def post_json(path, payload=None):
    return requests.post(f"{BASE}{path}", json=payload or {}, timeout=30).json()

def close(u,v,both=True): return post_json("/close_edge/", {"u":str(u),"v":str(v),"both":both})
def reverse(u,v):         return post_json("/reverse_edge/", {"u":str(u),"v":str(v)})
def reset():              return post_json("/reset_graph/")

# Ensure clean baseline
reset()

# Baseline matrix
baseline = {(s,t): sp(s,t) for (s,t) in OD}

with open("week2_api_scenarios.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["scenario","u","v","od_pairs","mean_delta_m","max_delta_m","num_disconnected"])
    for (u,v) in CAND:
        # ---- Closure ----
        reset(); close(u,v,True)
        deltas=[]; disc=0
        for (s,t) in OD:
            b = baseline[(s,t)]
            d = sp(s,t)
            if b is None:   # skip ODs that lack a baseline
                continue
            if d is None:   # disconnected under scenario
                disc += 1
            else:
                deltas.append(d - b)
        finite = [x for x in deltas if x is not None and math.isfinite(x)]
        mean_delta = (sum(finite)/len(finite)) if finite else 0.0
        max_delta  = max(finite) if finite else 0.0
        w.writerow(["closure",u,v,len(OD), f"{mean_delta:.3f}", f"{max_delta:.3f}", disc])

        # ---- Reversal ----
        reset(); reverse(u,v)
        deltas=[]; disc=0
        for (s,t) in OD:
            b = baseline[(s,t)]
            d = sp(s,t)
            if b is None: continue
            if d is None: disc += 1
            else: deltas.append(d - b)
        finite = [x for x in deltas if x is not None and math.isfinite(x)]
        mean_delta = (sum(finite)/len(finite)) if finite else 0.0
        max_delta  = max(finite) if finite else 0.0
        w.writerow(["reversal",u,v,len(OD), f"{mean_delta:.3f}", f"{max_delta:.3f}", disc])

reset()
print("Wrote week2_api_scenarios.csv")
