from utils import get_redis_connection
from config import QUEUE_NAME
import json


def inspect_queue():
    r = get_redis_connection()

    count = r.llen(QUEUE_NAME)
    print(f"--- QUEUE INSPECTION: {QUEUE_NAME} ---")
    print(f"Total messages: {count}")

    if count > 0:
        items = r.lrange(QUEUE_NAME, 0, -1)

        print("\nFirst 5 messages in queue:")
        for i, item in enumerate(items[:5]):
            data = json.loads(item)
            print(f"[{i + 1}] URL: {data['url']}")
            print(f"    Save to: {data['save_path']}")
            print("-" * 30)
    else:
        print("Queue is empty.")


if __name__ == "__main__":
    inspect_queue()