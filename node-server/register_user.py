from config import config
import requests

print(f"目前设置center:{config.center_host}:{config.center_port}")
print(f"目前设置local:{config.Host}:{config.Port}")

print("是否正确设置？(y/n)")

is_correct = input()
if is_correct == "n":
    print("请重新设置")

print("请输入注册的用户名:")
username = input()
print("请输入注册的密码:")
password = input()
print("请重复输入密码:")
password2 = input()

if password != password2:
    print("两次密码不一致")
    exit()

register_info = {
    "username": username,
    "password": password,
    "ip": config.Host,
    "port": config.Port,
}

res = requests.post(
    f"http://{config.center_host}:{config.center_port}/register", json=register_info
)
if res.status_code == 200:
    print("注册成功")
else:
    print(f"注册失败,{res.text}")
