import json
import networkx as nx

# 1. Load the JSON edge list
with open("berkeley_edge_list.json", "r", encoding="utf-8") as f:
    edges = json.load(f)

# 2. Build the directed graph
G = nx.DiGraph()
for e in edges:
    s, t, w = int(e["source"]), int(e["target"]), float(e["weight"])
    G.add_edge(s, t, weight=w)
    if e.get("bidirectional", False):
        G.add_edge(t, s, weight=w)

print(f"Graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.\n")

# 3. Interactive loop
while True:
    try:
        start_node = int(input("Enter start_node_id: "))
        end_node = int(input("Enter end_node_id: "))

        if start_node not in G or end_node not in G:
            print("One or both node IDs not found in the graph. Try again.\n")
            continue

        # 4. Compute shortest path
        path = nx.shortest_path(G, start_node, end_node, weight="weight")
        total_distance = nx.shortest_path_length(G, start_node, end_node, weight="weight")

        print("\nShortest path found:")
        print(" -> ".join(map(str, path)))
        print(f"Total distance: {total_distance:.3f} meters ({total_distance/1000:.3f} km)\n")

    except nx.NetworkXNoPath:
        print("No path exists between those nodes.\n")

    except ValueError:
        print("Invalid input. Please enter integer node IDs.\n")

    # 5. Continue or quit
    again = input("Do you want to test another pair? (y/n): ").lower()
    if again != "y":
        break

print("\nProgram finished.")
