import time
import threading
from custom_queue import Queue


# ---------------------------------------------------------------------------
# State Machine
# ---------------------------------------------------------------------------

# Valid statuses and their allowed next transition
STATUS_TRANSITIONS = {
    "Not Shipped":        "In-Transit",
    "In-Transit":         "Waiting to Offload",
    "Waiting to Offload": "Offloaded",
    "Offloaded":          None,          # Terminal state — no further transitions
}

# Ordered list used for display purposes
STATUS_ORDER = list(STATUS_TRANSITIONS.keys())


def next_status(current: str) -> str | None:
    """
    Return the next valid status for a given current status.
    Returns None if the order has reached its terminal state.
    Raises ValueError if an unknown status is provided.
    """
    if current not in STATUS_TRANSITIONS:
        raise ValueError(f"Unknown status: '{current}'")
    return STATUS_TRANSITIONS[current]


# ---------------------------------------------------------------------------
# Orders data
# ---------------------------------------------------------------------------

ORDERS = [
    {"order_id": "68862131", "destination": "Cairo"},
    {"order_id": "68862132", "destination": "Dubai"},
    {"order_id": "68862133", "destination": "Jeddah"},
    {"order_id": "68862134", "destination": "Ryadh"},
    {"order_id": "68862135", "destination": "Luxor"},
]


# ---------------------------------------------------------------------------
# Helper — pretty printing
# ---------------------------------------------------------------------------

SEPARATOR = "-" * 55

def print_status(order, event="UPDATE"):
    print(f"[{event}] ORD-{order['order_id']} | {order['destination']} | Status: {order['status']}")


# ---------------------------------------------------------------------------
# Thread 1 — Order Generator (Producer)
# ---------------------------------------------------------------------------

def generate_orders(q: Queue, total_orders: int):
    """
    Producer thread.
    Generates one shipment order per second, sets its initial status
    to 'Not Shipped', and pushes it into the shared queue.
    """
    print(SEPARATOR)
    print(" ORDER GENERATOR STARTED")
    print(SEPARATOR)

    for order_data in ORDERS:
        # Attach initial status to the order dict
        order = {**order_data, "status": "Not Shipped"}
        print_status(order, event="DISPATCH")
        q.enqueue(order)
        time.sleep(1)

    print(f"\n[GENERATOR] All {total_orders} orders dispatched.\n")


# ---------------------------------------------------------------------------
# Thread 2 — Order Processor (Consumer)
# ---------------------------------------------------------------------------

def process_orders(q: Queue, total_orders: int):
    """
    Consumer thread.
    Dequeues orders and advances each one through every status stage
    sequentially, enforced by the state machine.
    Each status transition takes 1.5 seconds to simulate real processing time.
    Starts 2 seconds after the generator to allow initial orders to queue up.
    """
    time.sleep(2)   # Let the producer get a head start

    print(SEPARATOR)
    print(" ORDER PROCESSOR STARTED")
    print(SEPARATOR)

    processed = 0

    while processed < total_orders:
        if not q.is_empty():
            order = q.dequeue()

            print(f"\n[PROCESS ] Picked up ORD-{order['order_id']} → destination: {order['destination']}")

            # Advance through every remaining status stage
            while order["status"] != "Offloaded":
                new_status = next_status(order["status"])
                order["status"] = new_status
                print_status(order, event="UPDATE")
                time.sleep(1.5)   # Simulate transit/handling time per stage

            print(f"[DONE    ] ORD-{order['order_id']} successfully offloaded at {order['destination']}.")
            print(SEPARATOR)
            processed += 1

        else:
            # Queue temporarily empty — wait for producer to add more
            time.sleep(0.5)

    print(f"\n✅ All {total_orders} orders have been delivered and offloaded.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    total = len(ORDERS)
    shared_queue = Queue()

    print("\n🚚 LOGISTICS TRACKING SYSTEM — STARTING\n")

    t1 = threading.Thread(target=generate_orders, args=(shared_queue, total), name="OrderGenerator")
    t2 = threading.Thread(target=process_orders,  args=(shared_queue, total), name="OrderProcessor")

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("\n🏁 All shipments processed. System shutting down.")