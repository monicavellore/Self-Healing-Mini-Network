import subprocess
import sys
import time


# --------------------------------------------------
# Start a Python component
# --------------------------------------------------

def start_component(script):

    print(f"Starting {script}...")

    process = subprocess.Popen(
        [sys.executable, script]
    )

    return process


# --------------------------------------------------
# Main system
# --------------------------------------------------

print("===================================")
print("   SELF-HEALING MINI NETWORK")
print("===================================")
print()


processes = []


try:

    # --------------------------------------------------
    # Start network nodes
    # --------------------------------------------------

    print("Starting network nodes...\n")

    processes.append(
        start_component("nodes/node.py")
    )

    processes.append(
        start_component("nodes/node_b.py")
    )

    processes.append(
        start_component("nodes/node_c.py")
    )

    processes.append(
        start_component("nodes/node_d.py")
    )

    # Give nodes time to start
    time.sleep(3)


    # --------------------------------------------------
    # Start network monitor
    # --------------------------------------------------

    print("\nStarting network monitor...\n")

    processes.append(
        start_component("monitor/monitor.py")
    )


    # --------------------------------------------------
    # Start network visualizer
    # --------------------------------------------------

    print("\nStarting network visualizer...\n")

    processes.append(
        start_component(
            "visualizer/network_visualizer.py"
        )
    )


    # Give monitor and visualizer time to start
    time.sleep(3)


    # --------------------------------------------------
    # Start self-healing router
    # --------------------------------------------------

    print("\nStarting self-healing router...\n")

    processes.append(
        start_component(
            "controller/router.py"
        )
    )


    # --------------------------------------------------
    # System status
    # --------------------------------------------------

    print("\n===================================")
    print("   NETWORK SYSTEM STARTED")
    print("===================================")

    print("\nComponents running:")
    print("✓ Node A")
    print("✓ Node B")
    print("✓ Node C")
    print("✓ Node D")
    print("✓ Network Monitor")
    print("✓ Network Visualizer")
    print("✓ Self-Healing Router")

    print("\nPress Ctrl+C to stop the system.")


    # --------------------------------------------------
    # Keep main program running
    # --------------------------------------------------

    while True:

        time.sleep(1)


except KeyboardInterrupt:

    print("\n\nStopping network system...")


finally:

    # --------------------------------------------------
    # Stop all components
    # --------------------------------------------------

    for process in processes:

        if process.poll() is None:

            process.terminate()

    print("All components stopped.")