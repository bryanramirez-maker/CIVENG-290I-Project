# week2_api_path_impact.py
import requests, csv, math, os

# === CONFIGURATION ===
# BASE = "https://two90i-assignment3-kfbu.onrender.com"  # FastAPI endpoint
BASE = "http://127.0.0.1:8000" #New Base
GRAPH_PATH = "berkeley_edge_list_aug.json"              # local JSON graph file
OD = [(0, 100), (8, 67), (11, 861), (67, 100), (50, 900)]  # origin-destination pairs
K = 10  # number of edges along the baseline path to test
OUT_CSV = "week2_api_path_impact.csv"

# === STEP 1: Upload the graph ===
with open(GRAPH_PATH, "rb") as f:
    r = requests.post(f"{BASE}/upload_graph_json/", files={"file": (GRAPH_PATH, f, "application/json")})
print("Uploaded:", r.json())

# === STEP 2: Prepare CSV output ===
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["scenario", "s", "t", "u", "v", "both", "baseline_m", "scenario_m", "delta_m"])

    # === STEP 3: Loop over all OD pairs ===
    for (s, t) in OD:
        # --- Baseline shortest path ---
        baseline = requests.get(f"{BASE}/solve_shortest_path/start_node_id={s}&end_node_id={t}").json()

        if "total_distance" not in baseline or baseline["total_distance"] is None:
            print(f"Skipping {s}->{t}: disconnected baseline.")
            continue

        base_dist = float(baseline["total_distance"])
        path = [int(x) for x in baseline["shortest_path"]]
        print(f"Baseline {s}->{t}: {base_dist:.3f} m, path len={len(path)}")

        # --- Select edges along the baseline path ---
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        K_eff = min(K, len(path_edges))
        edges_to_test = path_edges[:K_eff]

        # --- Run closure and reversal tests for each edge on the path ---
        for (u, v) in edges_to_test:
            for scenario in ["closure", "reversal"]:
                try:
                    # Call API with closure/reversal parameters
                    scenario_call = requests.get(
                        f"{BASE}/solve_shortest_path/start_node_id={s}&end_node_id={t}",
                        params={"u": u, "v": v, "scenario": scenario}
                    )
                    r_json = scenario_call.json()

                    if "total_distance" not in r_json or r_json["total_distance"] is None:
                        writer.writerow([scenario, s, t, u, v, scenario == "closure", base_dist, None, math.inf])
                        continue

                    new_dist = float(r_json["total_distance"])
                    delta = new_dist - base_dist
                    writer.writerow([scenario, s, t, u, v, scenario == "closure", base_dist, new_dist, delta])

                except Exception as e:
                    writer.writerow([scenario, s, t, u, v, scenario == "closure", base_dist, None, f"Error: {str(e)}"])

print(f"Wrote {OUT_CSV}")
