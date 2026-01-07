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
        logger.info(f"[Worker-{self.worker_id}] Initializare Chrome Driver...")
        options = uc.ChromeOptions()

        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        options.headless = False
        options.add_argument('--no-first-run')
        options.add_argument('--blink-settings=imagesEnabled=false')

        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            logger.error(f"[Worker-{self.worker_id}]  Nu s-a putut porni Chrome: {e}")
            sys.exit(1)

    def download_page(self, url, save_path):
        """Descarcă pagina folosind Browserul Real."""
        try:
            logger.info(f"[Worker-{self.worker_id}]  Navigare la: {url}")

            self.driver.get(url)
            time.sleep(5)

            page_content = self.driver.page_source

            if len(page_content) < 500:
                logger.warning(
                    f"[Worker-{self.worker_id}] Conținut suspect de mic ({len(page_content)} bytes). Posibil blocaj.")
                return False

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(page_content)

            logger.info(f"[Worker-{self.worker_id}] SUCCES: {os.path.basename(save_path)}")
            self.redis.incr("stats:success")
            return True

        except WebDriverException as e:
            logger.warning(f"[Worker-{self.worker_id}] Eroare Browser: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"[Worker-{self.worker_id}] Eroare Necunoscută: {e}")
            return False

    def handle_failure(self, task):
        """Logica de Retry."""
        current_retries = task.get('retry_count', 0)
        self.redis.incr("stats:retries")

        if current_retries < MAX_RETRIES:
            task['retry_count'] = current_retries + 1
            self.redis.rpush(QUEUE_NAME, json.dumps(task))
            logger.info(f"[Worker-{self.worker_id}] RE-QUEUED (Încercarea {task['retry_count']}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
        else:
            logger.error(f"[Worker-{self.worker_id}] EȘEC DEFINITIV: {task['url']}")
            self.redis.incr("stats:failed")

    def start(self):
        logger.info(f"[Worker-{self.worker_id}] Gata de treabă!")

        while True:
            packed = self.redis.blpop(QUEUE_NAME, timeout=10)

            if not packed:
                logger.info(f"[Worker-{self.worker_id}] STOP (Coada goala).")
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
            self.driver.quit()
        logger.info(f"Worker-{self.worker_id} terminat.")


if __name__ == "__main__":
    w_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    DownloadWorker(w_id).start()