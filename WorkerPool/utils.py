import redis
import logging
import sys
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WorkerPool")

def get_redis_connection():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        r.ping()
        logger.info("Conexiune la Redis realizată cu succes!")
        return r
    except redis.ConnectionError:
        logger.error("Nu mă pot conecta la Redis. Asigură-te că serverul rulează.")
        sys.exit(1)