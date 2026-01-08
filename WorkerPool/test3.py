import json
import sys
from utils import get_redis_connection
from config import QUEUE_NAME


def test_queue_content():
    print("--- PHASE 3: Queue Metadata Verification ---")
    r = get_redis_connection()

    length = r.llen(QUEUE_NAME)
    print(f"Elements in queue: {length}")

    if length == 0:
        print("WARNING: Queue is empty. Run 'python master.py' first.")
        sys.exit(1)

    item_raw = r.lrange(QUEUE_NAME, 0, 0)[0]

    try:
        data = json.loads(item_raw)

        if 'url' in data and 'save_path' in data:
            print("JSON Format: Valid")
            print(f"URL detected: {data['url']}")
            print("PHASE 3 SUCCESS: Valid tasks in queue.")
        else:
            print("ERROR: Missing keys in JSON.")

    except json.JSONDecodeError:
        print("ERROR: Malformed message (not JSON).")


if __name__ == "__main__":
    test_queue_content()