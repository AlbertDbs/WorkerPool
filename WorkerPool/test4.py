import os
import json
from worker import DownloadWorker
from utils import get_redis_connection
from config import QUEUE_NAME, DOWNLOAD_DIR


def test_single_download():
    print("--- PHASE 4: Test Worker Download ---")

    test_file = os.path.join(DOWNLOAD_DIR, "test_phase4.html")
    if os.path.exists(test_file):
        os.remove(test_file)

    task = {
        "url": "https://example.com",
        "save_path": test_file
    }

    r = get_redis_connection()
    r.lpush(QUEUE_NAME, json.dumps(task))
    print("Test task added to queue.")

    print("Starting worker for test...")
    worker = DownloadWorker(worker_id="Test-4")

    packed = r.blpop(QUEUE_NAME, timeout=5)
    if packed:
        _, msg = packed
        t = json.loads(msg)
        worker.download_page(t['url'], t['save_path'])
        worker.driver.quit()
    else:
        print("ERROR: Could not read task.")
        return

    if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
        print(f"File saved: {test_file}")
        print("PHASE 4 SUCCESS: Worker downloads and saves.")
    else:
        print("ERROR: File is missing or empty.")


if __name__ == "__main__":
    test_single_download()