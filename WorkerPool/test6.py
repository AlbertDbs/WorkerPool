import os
import sys
from utils import get_redis_connection
from config import LOG_DIR


def test_observability():
    print("--- PHASE 6: Test Logging & Statistics ---")

    log_file = os.path.join(LOG_DIR, 'app.log')
    if os.path.exists(log_file):
        size = os.path.getsize(log_file)
        print(f"Log file found: {size} bytes")
    else:
        print("ERROR: app.log file missing.")
        sys.exit(1)

    r = get_redis_connection()
    success = r.get("stats:success")
    failed = r.get("stats:failed")

    if success is not None or failed is not None:
        print(f"Redis statistics present -> Success: {success}, Failed: {failed}")
        print("PHASE 6 SUCCESS: Logging and monitoring active.")
    else:
        print("ERROR: Missing statistics keys in Redis.")


if __name__ == "__main__":
    test_observability()