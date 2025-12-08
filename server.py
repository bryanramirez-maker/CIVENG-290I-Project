# server.py
from fastapi import FastAPI, UploadFile, File
from typing import Optional
import uvicorn
import numpy as np
import math
import copy
import sys
sys.setrecursionlimit(100000)  # Increase limit significantly
from utils import create_graph_from_json
from dijkstra import dijkstra

app = FastAPI()
active_graph = None

@app.get("/")
async def root():
    return {"message": "Shortest Path Solver"}

@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile = File(...)):
    global active_graph
    try:
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": str(e)}

@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(
    start_node_id: str,
    end_node_id: str,
    u: Optional[str] = None,
    v: Optional[str] = None,
    scenario: Optional[str] = None
):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph loaded."}

    # 1. Force IDs to Strings
    s_id, t_id = str(start_node_id), str(end_node_id)
    if s_id not in active_graph.nodes or t_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}

    # 2. Deepcopy the graph
    G = copy.deepcopy(active_graph)

    # 3. Helper to find and delete edge by ID
    def remove_edge_by_id(source_node, target_id_str):
        target_obj = None
        for neighbor in source_node.neighbors:
            if str(neighbor.id) == target_id_str:
                target_obj = neighbor
                break
        if target_obj:
            del source_node.neighbors[target_obj]
            return target_obj
        return None

    # 4. Apply Scenario
    if u and v and scenario:
        u_id, v_id = str(u), str(v)
        
        if u_id in G.nodes and v_id in G.nodes:
            u_node = G.nodes[u_id]
            v_node = G.nodes[v_id]
            print(f"DEBUG: Applying {scenario} to {u_id}->{v_id}")

            if scenario == "closure":
                remove_edge_by_id(u_node, v_id) # Remove Forward
                remove_edge_by_id(v_node, u_id) # Remove Backward
            
            elif scenario == "reversal":
                target_obj = None
                for neighbor in u_node.neighbors:
                    if str(neighbor.id) == v_id:
                        target_obj = neighbor
                        break
                
                if target_obj:
                    weight = u_node.neighbors[target_obj]
                    del u_node.neighbors[target_obj]
                    v_node.neighbors[u_node] = weight

    # 5. Run Dijkstra
    dijkstra(G, G.nodes[s_id])
    
    end_node = G.nodes[t_id]
    if end_node.dist == np.inf or end_node.dist is None:
        return {"shortest_path": None, "total_distance": None}

    path = []
    cur = end_node
    while cur is not None:
        path.insert(0, cur.id)
        cur = cur.prev

    return {"shortest_path": path, "total_distance": float(end_node.dist)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
