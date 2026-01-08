import time
import json
import os
import sys
import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
from config import QUEUE_NAME, MAX_RETRIES, RETRY_DELAY
from utils import get_redis_connection, logger


class DownloadWorker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.redis = get_redis_connection()
        self.driver = None

        self.setup_driver()

    def setup_driver(self):
        logger.info(f"[Worker-{self.worker_id}] Initializing Chrome Driver...")
        options = uc.ChromeOptions()

        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        options.headless = False
        options.add_argument('--no-first-run')
        options.add_argument('--blink-settings=imagesEnabled=false')

        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            logger.error(f"[Worker-{self.worker_id}] Could not start Chrome: {e}")
            sys.exit(1)

    def restart_driver(self):
        logger.warning(f"[Worker-{self.worker_id}] CLOSED BROWSER DETECTED! Attempting restart...")

        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass

        time.sleep(2)
        self.setup_driver()
        logger.info(f"[Worker-{self.worker_id}] Browser restarted successfully! Continuing...")

    def download_page(self, url, save_path):
        try:
            logger.info(f"[Worker-{self.worker_id}] Navigating to: {url}")

            self.driver.get(url)

            time.sleep(5)

            page_content = self.driver.page_source

            if len(page_content) < 500:
                logger.warning(f"[Worker-{self.worker_id}] Content suspiciously small. Possible block.")
                return False

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(page_content)

            logger.info(f"[Worker-{self.worker_id}] SUCCESS: {os.path.basename(save_path)}")
            self.redis.incr("stats:success")
            return True

        except WebDriverException as e:
            error_msg = str(e).lower()
            logger.warning(f"[Worker-{self.worker_id}] Browser Error: {e.msg}")

            if "no such window" in error_msg or "target window already closed" in error_msg or "not found" in error_msg:
                self.restart_driver()

            return False

        except Exception as e:
            logger.error(f"[Worker-{self.worker_id}] Unknown Error: {e}")
            return False

    def handle_failure(self, task):
        current_retries = task.get('retry_count', 0)
        self.redis.incr("stats:retries")

        if current_retries < MAX_RETRIES:
            task['retry_count'] = current_retries + 1
            self.redis.rpush(QUEUE_NAME, json.dumps(task))
            logger.info(f"[Worker-{self.worker_id}] RE-QUEUED (Attempt {task['retry_count']}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
        else:
            logger.error(f"[Worker-{self.worker_id}] PERMANENT FAILURE: {task['url']}")
            self.redis.incr("stats:failed")

    def start(self):
        logger.info(f"[Worker-{self.worker_id}] Ready to work!")

        while True:
            packed = self.redis.blpop(QUEUE_NAME, timeout=10)

            if not packed:
                logger.info(f"[Worker-{self.worker_id}] STOP (Queue empty).")
                break

            _, message_json = packed
            try:
                task = json.loads(message_json)
            except json.JSONDecodeError:
                continue

            success = self.download_page(task['url'], task['save_path'])

            if not success:
                self.handle_failure(task)

            time.sleep(2)

        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        logger.info(f"Worker-{self.worker_id} finished.")


if __name__ == "__main__":
    w_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    DownloadWorker(w_id).start()