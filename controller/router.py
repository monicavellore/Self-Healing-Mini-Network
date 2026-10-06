import socket
import json
import networkx as nx
import time
import os
from datetime import datetime


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
# Load network topology
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
# Log configuration
# --------------------------------------------------

log_directory = "logs"

log_file = os.path.join(
    log_directory,
    "network_events.log"
)

os.makedirs(
    log_directory,
    exist_ok=True
)


# --------------------------------------------------
# Write event to log
# --------------------------------------------------

def log_event(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"[{timestamp}] ROUTER: {message}\n"
        )


# --------------------------------------------------
# Check whether a node is online
# --------------------------------------------------

def check_node(node):

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(1)

        sock.connect(
            ("127.0.0.1", node_ports[node])
        )

        sock.close()

        return True

    except:

        return False


# --------------------------------------------------
# Detect active nodes
# --------------------------------------------------

def get_active_network():

    active_nodes = []

    print("\nChecking network nodes...\n")

    for node in network.nodes:

        if check_node(node):

            active_nodes.append(node)

            print(
                f"Node {node}: ONLINE"
            )

        else:

            print(
                f"Node {node}: OFFLINE"
            )

    active_network = network.subgraph(
        active_nodes
    ).copy()

    print("\nActive Nodes:")
    print(active_nodes)

    return active_network


# --------------------------------------------------
# Find route from A to C
# --------------------------------------------------

def find_route(active_network):

    if (
        "A" not in active_network
        or "C" not in active_network
    ):

        print(
            "\nSource or destination node is offline."
        )

        log_event(
            "Source or destination node is offline"
        )

        return None

    if nx.has_path(
        active_network,
        "A",
        "C"
    ):

        path = nx.shortest_path(
            active_network,
            "A",
            "C"
        )

        # Console uses arrow symbol
        route_text = " → ".join(path)

        # Log uses ASCII arrow
        log_route_text = " -> ".join(path)

        print("\nSelected Route:")
        print(route_text)

        log_event(
            f"Route selected: {log_route_text}"
        )

        return path

    else:

        print(
            "\nNo available route from A to C."
        )

        log_event(
            "No available route from A to C"
        )

        return None


# --------------------------------------------------
# Send message with automatic rerouting
# --------------------------------------------------

def send_message(
    path,
    message,
    active_network
):

    if path is None:

        return False

    current_node = path[0]

    remaining_nodes = path[1:]

    print("\nSending message...")

    log_event(
        "Message delivery started"
    )

    while remaining_nodes:

        next_node = remaining_nodes[0]

        print(
            f"\nPreparing to contact Node {next_node}..."
        )

        print(
            "Waiting 5 seconds before connection..."
        )

        time.sleep(5)

        port = node_ports[next_node]

        try:

            client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            client.settimeout(2)

            client.connect(
                ("127.0.0.1", port)
            )

            client.send(
                message.encode()
            )

            response = client.recv(
                1024
            ).decode()

            print(
                f"Reached Node {next_node}: {response}"
            )

            log_event(
                f"Reached Node {next_node}: {response}"
            )

            client.close()

            # Move forward
            current_node = next_node

            remaining_nodes.pop(0)

        except:

            print(
                f"\nNode {next_node} became unreachable."
            )

            log_event(
                f"Node {next_node} became unreachable"
            )

            print(
                f"Removing Node {next_node} from network..."
            )

            log_event(
                f"Node {next_node} removed from active network"
            )

            # Remove failed node
            if next_node in active_network:

                active_network.remove_node(
                    next_node
                )

            # Find alternative route
            if (
                current_node in active_network
                and "C" in active_network
                and nx.has_path(
                    active_network,
                    current_node,
                    "C"
                )
            ):

                new_path = nx.shortest_path(
                    active_network,
                    current_node,
                    "C"
                )

                # Console uses arrow symbol
                route_text = " → ".join(
                    new_path
                )

                # Log uses ASCII arrow
                log_route_text = " -> ".join(
                    new_path
                )

                print(
                    "\nSelf-healing activated."
                )

                print(
                    "New Route:"
                )

                print(
                    route_text
                )

                log_event(
                    "Self-healing activated"
                )

                log_event(
                    f"New route selected: {log_route_text}"
                )

                # Continue from current node
                remaining_nodes = new_path[1:]

            else:

                print(
                    "\nNo alternative route available."
                )

                log_event(
                    "No alternative route available"
                )

                return False

    print(
        "\nMessage successfully delivered."
    )

    log_event(
        "Message successfully delivered"
    )

    return True


# --------------------------------------------------
# Long-running controller
# --------------------------------------------------

print("\n===================================")
print("   SELF-HEALING ROUTER CONTROLLER")
print("===================================")

print(
    "\nRouter is running continuously."
)

print(
    "Press ENTER to send a message."
)

print(
    "Type 'q' and press ENTER to stop."
)


log_event(
    "Router controller started"
)


# --------------------------------------------------
# Continuous operation
# --------------------------------------------------

try:

    while True:

        command = input(
            "\nRouter command: "
        )

        # Stop router
        if command.lower() == "q":

            print(
                "\nStopping router..."
            )

            log_event(
                "Router controller stopped"
            )

            break

        # Check current network
        active_network = get_active_network()

        # Find current route
        path = find_route(
            active_network
        )

        if path is None:

            print(
                "\nMessage cannot be sent."
            )

            continue

        # Send message
        send_message(
            path,
            "Hello from Self-Healing Network",
            active_network
        )


except KeyboardInterrupt:

    print(
        "\n\nRouter stopped."
    )

    log_event(
        "Router controller interrupted"
    )