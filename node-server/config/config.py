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
    Port = 8100

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

    # 数据管理中心
    center_host = "127.0.0.1"
    center_port = 8000

    # database config
    Redis_host = "10.211.55.14"
    Redis_port = 6379
    Redis_db = 0
    Redis_password = "password"


config = Config()
