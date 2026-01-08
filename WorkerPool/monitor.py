import time
import sys
from utils import get_redis_connection
from config import QUEUE_NAME


def show_dashboard():
    r = get_redis_connection()

    print("\n" * 2)
    print("========================================")
    print("   WORKER POOL MONITORING DASHBOARD     ")
    print("========================================")
    print("Press Ctrl+C to stop the monitor.\n")

    try:
        while True:
            total = int(r.get("stats:total_tasks") or 0)
            success = int(r.get("stats:success") or 0)
            failed = int(r.get("stats:failed") or 0)
            retries = int(r.get("stats:retries") or 0)

            queue_len = r.llen(QUEUE_NAME)

            processed = success + failed
            percent = (processed / total * 100) if total > 0 else 0

            sys.stdout.write("\033[K")
            print(f"\r PROGRESS: [{processed}/{total}] ({percent:.1f}%) | "
                  f" Success: {success} | "
                  f" Failed: {failed} | "
                  f" Retries: {retries} | "
                  f" Queue: {queue_len}", end="\r")

            sys.stdout.flush()
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")


if __name__ == "__main__":
    show_dashboard()