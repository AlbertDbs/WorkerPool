import os

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
QUEUE_NAME = 'download_queue'

MAX_RETRIES = 3
RETRY_DELAY = 2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)