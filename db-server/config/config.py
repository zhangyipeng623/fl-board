import logging

logging.basicConfig(
    filename=f"./log/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Config(object):

    # server config
    App = "app:app"
    Host = "127.0.0.1"
    Port = 8000

    Reload = True
    DEBUG = True

    logger = logging.getLogger("app")

    # cors config 跨域请求
    Origins = [
        "http://localhost:8080",  # 允许从前端应用的 URL 进行请求
        "http://127.0.0.1:8080",
        "*",  # 允许所有（可根据需要调整为特定域）
    ]
    Allow_methods = ["*"]
    Allow_headers = ["*"]

    # database config
    Redis_host = "192.168.3.106"
    Redis_port = 6379
    Redis_db = 0
    Redis_password = "password"

    Mysql_host = "192.168.3.106"
    Mysql_port = 3306
    Mysql_user = "fl"
    Mysql_password = "password"
    Mysql_db = "fl"


config = Config()
