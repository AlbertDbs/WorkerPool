import json
from utils import get_redis_connection, logger
from config import DOWNLOAD_DIR, QUEUE_NAME
import argparse
import time
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import logger
from config import DOWNLOAD_DIR


class MasterScheduler:
    def __init__(self, country='united-states'):
        self.start_url = f"https://www.semrush.com/website/top/{country}/all/"
        self.driver = None

    def setup_driver(self):
        options = uc.ChromeOptions()

        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        options.headless = False
        options.add_argument('--no-first-run')

        logger.info(f"Pornesc Chrome de la: {options.binary_location}")

        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True)
        except Exception as e:
            logger.error(f"Eroare critică la pornire Chrome: {e}")
            import sys
            sys.exit(1)

    def fetch_page_content(self):
        try:
            self.driver.get(self.start_url)
            logger.info(f"Navighez la: {self.start_url}")

            logger.info("Aștept încărcarea tabelului...")
            time.sleep(5)

            return self.driver.page_source
        except Exception as e:
            logger.error(f"Eroare în browser: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def parse_links(self, html_content):
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        tasks = []

        all_links = soup.find_all('a', href=True)

        unique_domains = set()

        for link in all_links:
            text = link.get_text().strip()
            href = link['href']

            if '.' in text and 'semrush' not in href and len(text) < 50:
                if text not in unique_domains:
                    unique_domains.add(text)

                    full_url = f"https://{text}"
                    file_name = f"semrush_{text.replace('.', '_')}.html"
                    save_path = os.path.join(DOWNLOAD_DIR, file_name)

                    tasks.append({
                        "url": full_url,
                        "save_path": save_path,
                        "source": "semrush"
                    })

                    if len(tasks) >= 20:
                        break

        return tasks

    def run(self):
        self.setup_driver()
        html = self.fetch_page_content()
        tasks = self.parse_links(html)

        if not tasks:
            logger.warning("Nu am găsit task-uri de procesat.")
            return

        logger.info(f"Mă conectez la Redis pentru a trimite {len(tasks)} task-uri...")
        try:
            r = get_redis_connection()
        except Exception:
            logger.error("Nu pot continua fără Redis.")
            return

        count = 0
        for task in tasks:
            try:
                message_json = json.dumps(task)

                r.rpush(QUEUE_NAME, message_json)

                logger.info(f"ENQUEUED: {task['url']}")
                count += 1
            except Exception as e:
                logger.error(f"Eroare la trimiterea task-ului {task['url']}: {e}")

        logger.info(f"Finalizat! Am trimis {count} task-uri în coada '{QUEUE_NAME}'.")

        q_len = r.llen(QUEUE_NAME)
        logger.info(f"Lungimea curentă a cozii Redis: {q_len}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--country', type=str, default='united-states',
                        help='Numele țării din URL (ex: united-states, romania)')
    args = parser.parse_args()

    # Verificăm să nu fie folderul gol
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    master = MasterScheduler(country=args.country)
    master.run()