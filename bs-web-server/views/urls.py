from fastapi import APIRouter
from fastapi import  HTTPException
from pydantic import BaseModel


router = APIRouter()

class LoginForm(BaseModel):
    username: str
    password: str

@router.post("/login") # 根路由
def login(form: LoginForm):
    if(form.username == "111"):
        return HTTPException(status_code=401, detail="用户名或密码错误")
    print(form.username, form.password)
    return {"session": "abcdef"}
