from fastapi import APIRouter,Request
from model import User
import requests

node = APIRouter(prefix="/node")

@node.get("/status")
def get_node(request: Request):
    username = request.query_params.get("username")
    user_list = User.select(User.username, User.ip, User.port).where(User.username != username).order_by(User.created_at.desc()).dicts()
    user_list = list(user_list)
    session = request.query_params.get("session")
    for user in user_list:
        user["name"] = user["username"]
        url = f"http://{user['ip']}:{user['port']}/status?session={session}"
        try:
            if requests.get(url, timeout=3).status_code == 200:
                user["is_connect"] = True
            else:
                user["is_connect"] = False
        except:
            user["is_connect"] = False
    return {"user_list": user_list}


