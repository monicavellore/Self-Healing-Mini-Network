import json
import socket
import time

import matplotlib.pyplot as plt
import networkx as nx


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TOPOLOGY_FILE = "nodes/topology.json"

NODE_PORTS = {
    "A": 5001,
    "B": 5002,
    "C": 5003,
    "D": 5004
}

REFRESH_INTERVAL = 5


# --------------------------------------------------
# Load topology
# --------------------------------------------------

with open(TOPOLOGY_FILE, "r") as file:
    topology = json.load(file)


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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        sock.connect(
            ("127.0.0.1", NODE_PORTS[node])
        )

        sock.close()
        return True

    except Exception:
        return False


# --------------------------------------------------
# Get current network state
# --------------------------------------------------

def get_network_state():
    online_nodes = []
    offline_nodes = []

    for node in network.nodes:
        if check_node(node):
            online_nodes.append(node)
        else:
            offline_nodes.append(node)

    active_network = network.subgraph(
        online_nodes
    ).copy()

    active_route = None

    if (
        "A" in active_network
        and "C" in active_network
        and nx.has_path(active_network, "A", "C")
    ):
        active_route = nx.shortest_path(
            active_network,
            "A",
            "C"
        )

    return online_nodes, offline_nodes, active_route


# --------------------------------------------------
# Draw network
# --------------------------------------------------

def draw_network(
    ax,
    online_nodes,
    offline_nodes,
    active_route
):
    ax.clear()

    positions = {
        "A": (-1, 0),
        "B": (0, 1),
        "C": (1, 0),
        "D": (0, -1)
    }

    # Draw all topology connections
    nx.draw_networkx_edges(
        network,
        positions,
        ax=ax,
        edge_color="lightgray",
        width=2
    )

    # Draw active route
    if active_route and len(active_route) > 1:
        route_edges = list(
            zip(
                active_route[:-1],
                active_route[1:]
            )
        )

        nx.draw_networkx_edges(
            network,
            positions,
            edgelist=route_edges,
            ax=ax,
            edge_color="black",
            width=5
        )

    # Draw online nodes
    if online_nodes:
        nx.draw_networkx_nodes(
            network,
            positions,
            nodelist=online_nodes,
            ax=ax,
            node_color="green",
            node_size=1800
        )

    # Draw offline nodes
    if offline_nodes:
        nx.draw_networkx_nodes(
            network,
            positions,
            nodelist=offline_nodes,
            ax=ax,
            node_color="white",
            node_size=1800,
            node_shape="X",
            edgecolors="red",
            linewidths=4
        )

    # Node labels
    nx.draw_networkx_labels(
        network,
        positions,
        ax=ax,
        font_size=18,
        font_weight="bold"
    )

    # Determine network status
    if active_route == ["A", "B", "C"]:
        network_status = "HEALTHY"

    elif active_route is not None:
        network_status = "SELF-HEALING"

    else:
        network_status = "NO ROUTE"

    # Title
    ax.set_title(
        "Self-Healing Mini Network",
        fontsize=20,
        pad=20
    )

    # Status information
    online_text = f"Online: {online_nodes}"
    offline_text = f"Offline: {offline_nodes}"

    if active_route:
        route_text = (
            "Active Route: "
            + " → ".join(active_route)
        )
    else:
        route_text = "Active Route: None"

    status_text = (
        f"{online_text}\n"
        f"{offline_text}\n"
        f"{route_text}\n"
        f"Network Status: {network_status}"
    )

    ax.text(
        -1.55,
        -1.35,
        status_text,
        fontsize=13,
        verticalalignment="top"
    )

    # Legend
    online_marker = plt.Line2D(
        [],
        [],
        marker="o",
        linestyle="None",
        markersize=12,
        markerfacecolor="green",
        markeredgecolor="green",
        label="Online Node"
    )

    offline_marker = plt.Line2D(
        [],
        [],
        marker="X",
        linestyle="None",
        markersize=12,
        markerfacecolor="white",
        markeredgecolor="red",
        markeredgewidth=3,
        label="Offline Node"
    )

    route_marker = plt.Line2D(
        [],
        [],
        color="black",
        linewidth=5,
        label="Active Route"
    )

    ax.legend(
        handles=[
            online_marker,
            offline_marker,
            route_marker
        ],
        loc="upper right",
        fontsize=11
    )

    ax.set_axis_off()

    # Keep a consistent view
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.6, 1.5)


# --------------------------------------------------
# Main visualizer
# --------------------------------------------------

def main():

    print("===================================")
    print("   SELF-HEALING NETWORK VISUALIZER")
    print("===================================")

    # IMPORTANT:
    # Create ONE figure only.
    # It will be reused for every refresh.
    plt.ion()

    fig, ax = plt.subplots(
        figsize=(10, 8)
    )

    fig.canvas.manager.set_window_title(
        "Self-Healing Mini Network"
    )

    try:

        while plt.fignum_exists(fig.number):

            online_nodes, offline_nodes, active_route = (
                get_network_state()
            )

            draw_network(
                ax,
                online_nodes,
                offline_nodes,
                active_route
            )

            # Redraw the SAME window
            fig.canvas.draw_idle()
            fig.canvas.flush_events()

            print("Network status updated.")

            # Keep the GUI responsive while waiting
            for _ in range(50):

                if not plt.fignum_exists(fig.number):
                    break

                plt.pause(REFRESH_INTERVAL / 50)

    except KeyboardInterrupt:

        print("\nVisualizer stopped.")

    finally:

        plt.close(fig)


# --------------------------------------------------
# Start
# --------------------------------------------------

if __name__ == "__main__":
    main()