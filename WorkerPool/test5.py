import json
import time
from worker import DownloadWorker
from utils import get_redis_connection
from config import QUEUE_NAME


def test_retry_logic():
    print("--- PHASE 5: Test Failure Recovery & Retry ---")

    r = get_redis_connection()
    r.delete(QUEUE_NAME)

    bad_url = "https://site-inexistent-test-network-fail.com"
    bad_task = {
        "url": bad_url,
        "save_path": "dummy_fail.html",
        "retry_count": 0
    }

    r.rpush(QUEUE_NAME, json.dumps(bad_task))
    print(f"1. Network-Fail task added: {bad_url}")

    print("2. Worker receives task...")
    worker = DownloadWorker(worker_id="Test-Fail-Recovery")

    packed = r.blpop(QUEUE_NAME, timeout=5)

    if packed:
        _, msg = packed
        t = json.loads(msg)

        print("   -> Attempting download...")
        success = worker.download_page(t['url'], t['save_path'])

        if success is False:
            print("   -> OK: Worker detected network issue (return False).")

            print("   -> Applying Retry logic...")
            worker.handle_failure(t)
        else:
            print("ERROR: Worker reported success on invalid link.")
            worker.driver.quit()
            return

        worker.driver.quit()
    else:
        print("ERROR: Empty queue.")
        return

    time.sleep(1)

    new_len = r.llen(QUEUE_NAME)
    if new_len > 0:
        item = r.lrange(QUEUE_NAME, 0, 0)[0]
        data = json.loads(item)

        if data['retry_count'] == 1:
            print(f"3. Queue Verification: Task successfully reinserted.")
            print(f"   Retry Count: {data['retry_count']} (Increased)")
            print("PHASE 5 SUCCESS: System handles network errors and retries.")
        else:
            print(f"ERROR: Incorrect retry count ({data.get('retry_count')}).")
    else:
        print("ERROR: Message lost (Message Loss).")


if __name__ == "__main__":
    test_retry_logic()