import json
import networkx as nx
import matplotlib.pyplot as plt

# === CONFIGURATION ===
GRAPH_PATH = "berkeley_edge_list_aug.json"

def plot_network():
    print("Loading graph data...")
    with open(GRAPH_PATH, 'r') as f:
        data = json.load(f)

    # Create a NetworkX graph
    G = nx.DiGraph()
    
    # Add edges
    for row in data:
        u, v = str(row['source']), str(row['target'])
        G.add_edge(u, v)

    print(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges.")
    print("Generating plot (this might take a moment)...")

    plt.figure(figsize=(12, 12))
    
    # Draw the graph
    # node_size=10 makes them small dots
    # width=0.2 makes the lines thin and elegant
    # arrowsize=5 makes the direction arrows subtle
    pos = nx.spring_layout(G, k=0.15, iterations=20) # 'k' controls spacing
    nx.draw_networkx_nodes(G, pos, node_size=10, node_color='black')
    nx.draw_networkx_edges(G, pos, width=0.2, alpha=0.5, arrowstyle='->', arrowsize=5)

    plt.title("Topology of the Berkeley Road Network", fontsize=15)
    plt.axis('off') # Turn off X/Y axis numbers
    
    plt.tight_layout()
    plt.savefig("berkeley_network_map.png", dpi=300) # High res for poster
    print("Saved 'berkeley_network_map.png'!")
    plt.show()

if __name__ == "__main__":
    plot_network()
