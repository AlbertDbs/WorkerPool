import time
import json
import requests
import os
import sys
from fake_useragent import UserAgent
from config import QUEUE_NAME
from utils import get_redis_connection, logger


class DownloadWorker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.redis = get_redis_connection()
        self.ua = UserAgent()

    def download_page(self, url, save_path):
        headers = {'User-Agent': self.ua.random}

        try:
            logger.info(f"[Worker-{self.worker_id}] Descarc: {url}")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info(f"[Worker-{self.worker_id}]  SALVAT: {os.path.basename(save_path)}")
                return True
            else:
                logger.error(f"[Worker-{self.worker_id}] Eroare HTTP {response.status_code} pentru {url}")
                return False

        except Exception as e:
            logger.error(f"[Worker-{self.worker_id}] Eroare rețea: {e}")
            return False

    def start(self):
        logger.info(f"Worker-{self.worker_id} a pornit și așteaptă task-uri...")

        while True:
            packed = self.redis.blpop(QUEUE_NAME, timeout=5)

            if not packed:
                logger.info(f"[Worker-{self.worker_id}] Coada este goală. Mă opresc.")
                break

            _, message_json = packed
            task = json.loads(message_json)

            self.download_page(task['url'], task['save_path'])

            time.sleep(1)

        logger.info(f"Worker-{self.worker_id} și-a terminat execuția.")


if __name__ == "__main__":
    w_id = sys.argv[1] if len(sys.argv) > 1 else "1"

    worker = DownloadWorker(worker_id=w_id)
    worker.start()