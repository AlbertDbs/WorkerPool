import sys
from utils import get_redis_connection


def test_connection():
    print("--- PHASE 1: Test Connectivity ---")
    try:
        r = get_redis_connection()
        print("Redis Connection: OK")

        test_queue = "test_phase1_queue"
        r.delete(test_queue)

        r.rpush(test_queue, "test_message")
        print("Enqueue (Push): OK")

        item = r.lpop(test_queue)
        if item == "test_message":
            print("Dequeue (Pop): OK")
            print("PHASE 1 SUCCESS: System communicates with queue.")
        else:
            print("ERROR: Incorrect message received.")
            sys.exit(1)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()