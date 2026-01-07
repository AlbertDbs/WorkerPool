import redis
import logging
import sys
import os
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, LOG_DIR

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger = logging.getLogger("WorkerPool")
logger.setLevel(logging.INFO)
logger.handlers = []

formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'app.log'), encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_redis_connection():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        # Test rapid
        r.ping()
        return r
    except redis.ConnectionError:
        logger.error("Nu se poate conecta la Redis. Serverul rulează?")
        sys.exit(1)