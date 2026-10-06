import socket
import json
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
# Log file
# --------------------------------------------------

log_directory = "logs"
log_file = os.path.join(
    log_directory,
    "network_events.log"
)

os.makedirs(log_directory, exist_ok=True)


# --------------------------------------------------
# Store previous node status
# --------------------------------------------------

previous_status = {}


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
# Write event to log
# --------------------------------------------------

def log_event(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(log_file, "a") as file:

        file.write(
            f"[{timestamp}] {message}\n"
        )


# --------------------------------------------------
# Monitor network
# --------------------------------------------------

def monitor_network():

    global previous_status

    print("\n===================================")
    print("     SELF-HEALING NETWORK MONITOR")
    print("===================================")

    online_nodes = []
    offline_nodes = []

    for node in topology["nodes"]:

        online = check_node(node)

        # Current status
        if online:

            online_nodes.append(node)

            current_status = "ONLINE"

            print(
                f"Node {node}: ONLINE"
            )

        else:

            offline_nodes.append(node)

            current_status = "OFFLINE"

            print(
                f"Node {node}: OFFLINE"
            )

        # Detect status changes
        if node in previous_status:

            if previous_status[node] != current_status:

                event = (
                    f"Node {node} changed from "
                    f"{previous_status[node]} to "
                    f"{current_status}"
                )

                log_event(event)

                print(
                    f"EVENT LOGGED: {event}"
                )

        else:

            # Log initial status
            log_event(
                f"Node {node} detected as "
                f"{current_status}"
            )

        previous_status[node] = current_status

    print("\n-----------------------------------")

    print(
        f"Online Nodes : {online_nodes}"
    )

    print(
        f"Offline Nodes: {offline_nodes}"
    )

    print("-----------------------------------")


# --------------------------------------------------
# Continuous monitoring
# --------------------------------------------------

try:

    while True:

        monitor_network()

        print(
            "\nNext health check in 5 seconds..."
        )

        time.sleep(5)

except KeyboardInterrupt:

    print(
        "\nMonitoring stopped."
    )