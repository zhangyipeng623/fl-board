
class Config(object):

    # server config
    App = "main:app"
    Host = "localhost"
    Port = 8000

    Reload = True
    DEBUG = True
    

    # cors config 跨域请求
    Origins = [
    "http://localhost:8080",  # 允许从前端应用的 URL 进行请求
    "http://127.0.0.1:8080",
    "*",  # 允许所有（可根据需要调整为特定域）
    ]
    Allow_methods = ["*"]
    Allow_headers = ["*"]


    # database config
    Redis_host = "10.211.55.12"
    Redis_port = 6379
    Redis_db = 0
    Redis_password = "password"

    Mysql_host = "10.211.55.12"
    Mysql_port = 3306
    Mysql_user = "root"
    Mysql_password = "password"
    Mysql_db = "fl"



config = Config()