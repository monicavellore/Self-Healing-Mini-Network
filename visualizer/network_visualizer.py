import socket
import json
import time
import matplotlib.pyplot as plt
import networkx as nx


# --------------------------------------------------
# Node ports
# --------------------------------------------------

node_ports = {
    "A": 5001,
    "B": 5002,
    "C": 5003,
    "D": 5004
}


# --------------------------------------------------
# Load topology
# --------------------------------------------------

with open("nodes/topology.json", "r") as file:
    topology = json.load(file)


# --------------------------------------------------
# Create network graph
# --------------------------------------------------

network = nx.Graph()

for node in topology["nodes"]:
    network.add_node(node)

for connection in topology["connections"]:
    network.add_edge(connection[0], connection[1])


# --------------------------------------------------
# Check node status
# --------------------------------------------------

def check_node(node):

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(0.5)

        sock.connect(
            ("127.0.0.1", node_ports[node])
        )

        sock.close()

        return True

    except:
        return False


# --------------------------------------------------
# Find active route
# --------------------------------------------------

def find_active_route(online_nodes):

    active_network = network.subgraph(
        online_nodes
    ).copy()

    try:

        route = nx.shortest_path(
            active_network,
            source="A",
            target="C"
        )

        return route

    except nx.NetworkXNoPath:

        return []


# --------------------------------------------------
# Determine network status
# --------------------------------------------------

def get_network_status(online_nodes, active_route):

    if not active_route:
        return "NO ROUTE"

    if active_route == ["A", "B", "C"]:
        return "HEALTHY"

    return "SELF-HEALING"


# --------------------------------------------------
# Draw network
# --------------------------------------------------

def draw_network():

    online_nodes = []
    offline_nodes = []

    # Check every node
    for node in network.nodes:

        if check_node(node):
            online_nodes.append(node)

        else:
            offline_nodes.append(node)

    # Find current active route
    active_route = find_active_route(
        online_nodes
    )

    # Determine network status
    network_status = get_network_status(
        online_nodes,
        active_route
    )

    # Clear previous visualization
    plt.clf()

    # Fixed positions
    positions = {
        "A": (-1, 0),
        "B": (0, 1),
        "C": (1, 0),
        "D": (0, -1)
    }

    # --------------------------------------------------
    # Draw all topology connections
    # --------------------------------------------------

    nx.draw_networkx_edges(
        network,
        positions,
        width=2,
        alpha=0.4
    )

    # --------------------------------------------------
    # Draw active route
    # --------------------------------------------------

    if len(active_route) >= 2:

        route_edges = list(
            zip(
                active_route,
                active_route[1:]
            )
        )

        nx.draw_networkx_edges(
            network,
            positions,
            edgelist=route_edges,
            width=4
        )

    # --------------------------------------------------
    # Draw online nodes
    # --------------------------------------------------

    if online_nodes:

        nx.draw_networkx_nodes(
            network,
            positions,
            nodelist=online_nodes,
            node_size=1800,
            node_color="green"
        )

    # --------------------------------------------------
    # Draw offline nodes
    # --------------------------------------------------

    if offline_nodes:

        nx.draw_networkx_nodes(
            network,
            positions,
            nodelist=offline_nodes,
            node_size=1800,
            node_shape="X",
            node_color="red"
        )

    # --------------------------------------------------
    # Draw node names
    # --------------------------------------------------

    nx.draw_networkx_labels(
        network,
        positions,
        font_size=14,
        font_weight="bold"
    )

    # --------------------------------------------------
    # Display route
    # --------------------------------------------------

    if active_route:

        route_text = " → ".join(
            active_route
        )

    else:

        route_text = "No route available"

    # --------------------------------------------------
    # Display network information
    # --------------------------------------------------

    plt.title(
        "Self-Healing Mini Network"
    )

    plt.text(
        -1.5,
        -1.5,
        f"Online: {online_nodes}\n"
        f"Offline: {offline_nodes}\n"
        f"Active Route: {route_text}\n"
        f"Network Status: {network_status}",
        fontsize=11
    )

    # --------------------------------------------------
    # Legend
    # --------------------------------------------------

    online_legend = plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Online Node",
        markerfacecolor="green",
        markersize=12
    )

    offline_legend = plt.Line2D(
        [0],
        [0],
        marker="X",
        color="w",
        label="Offline Node",
        markerfacecolor="red",
        markersize=12
    )

    route_legend = plt.Line2D(
        [0],
        [0],
        color="black",
        linewidth=4,
        label="Active Route"
    )

    plt.legend(
        handles=[
            online_legend,
            offline_legend,
            route_legend
        ],
        loc="upper right"
    )

    plt.axis("off")

    plt.pause(0.1)


# --------------------------------------------------
# Start visualization
# --------------------------------------------------

plt.ion()

figure = plt.figure(
    figsize=(8, 6)
)

print("\n===================================")
print("   SELF-HEALING NETWORK VISUALIZER")
print("===================================")

try:

    while True:

        draw_network()

        print(
            "Network status updated."
        )

        time.sleep(5)

except KeyboardInterrupt:

    print(
        "\nVisualizer stopped."
    )

    plt.ioff()
    plt.close()