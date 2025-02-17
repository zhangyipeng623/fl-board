import redis as r
from config import config

pool = r.ConnectionPool(
    host=config.Redis_host,
    port=config.Redis_port,
    db=config.Redis_db,
    password=config.Redis_password,
)
redis = r.Redis(connection_pool=pool)
