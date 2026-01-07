from utils import get_redis_connection
from config import QUEUE_NAME
import json


def inspect_queue():
    r = get_redis_connection()

    count = r.llen(QUEUE_NAME)
    print(f"--- INSPECTIE COADA: {QUEUE_NAME} ---")
    print(f"Mesaje totale: {count}")

    if count > 0:
        items = r.lrange(QUEUE_NAME, 0, -1)

        print("\nPrimele 5 mesaje din coada:")
        for i, item in enumerate(items[:5]):
            data = json.loads(item)
            print(f"[{i + 1}] URL: {data['url']}")
            print(f"    Salvare in: {data['save_path']}")
            print("-" * 30)
    else:
        print("Coada este goala.")


if __name__ == "__main__":
    inspect_queue()