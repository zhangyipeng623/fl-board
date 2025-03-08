import json
import uuid
import os
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from model import redis
from config import config

router = APIRouter()


class LoginForm(BaseModel):
    id: int
    username: str
    ip: str
    port: int
    session: str


@router.post("/login")  # 根路由
def login(form: LoginForm, request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host
    if ip != config.center_host:
        raise HTTPException(401, detail="用户未登录")
    user_info = json.dumps(
        {"username": form.username, "id": form.id, "ip": form.ip, "port": form.port}
    )
    redis.set(form.session, user_info, ex=60 * 60 * 24 * 2)
    return {"status": "ok"}


@router.get("/status")
def get_status():
    status = {"mysql": False, "redis": False, "nginx": False}
    # ---------- 检查 Redis 连接 ----------
    try:
        # 使用更具体的异常类型（如 redis.ConnectionError）
        redis.ping()  # 假设 redis_client 是已配置的客户端
        status["redis"] = True
    except Exception as e:
        config.logger.error("Redis 连接失败: %s", e)
        status["redis"] = False

    return {"data": status}


@router.get("/check_session")
def check_session(request: Request):
    session = request.headers.get("Authorization")
    user_info = redis.get(session)
    if user_info is None:
        raise HTTPException(401, detail="用户未登录")
    return user_info


@router.get("/logout")
def logout(request: Request):
    session = request.headers.get("Authorization")
    redis.delete(session)
    return {"message": "用户已退出"}


# 存储活跃的上传会话
active_uploads = {}


@router.websocket("/upload_big_file")
async def websocket_upload(websocket: WebSocket):
    await websocket.accept()
    file_id = None
    temp_file = None

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "start":
                # 生成唯一文件名
                file_id = str(uuid.uuid4())
                file_ext = message.get("fileType", "")
                file_name = f"{file_id}.{file_ext}"

                # 创建临时文件
                upload_dir = "static/uploads/temp"
                os.makedirs(upload_dir, exist_ok=True)
                temp_path = os.path.join(upload_dir, file_name)

                temp_file = open(temp_path, "wb")

                # 存储上传信息
                active_uploads[file_id] = {
                    "path": temp_path,
                    "metadata": message.get("metadata", {}),
                    "total_chunks": message.get("totalChunks", 0),
                    "received_chunks": 0,
                    "original_filename": message.get("fileName", "unknown")
                }

                # 返回文件ID
                await websocket.send_json({
                    "type": "start",
                    "filename": file_id
                })

            elif message["type"] == "chunk":
                if not file_id or file_id != message.get("filename"):
                    await websocket.send_json({
                        "type": "error",
                        "message": "无效的文件ID"
                    })
                    continue

                # 接收二进制数据
                binary_data = await websocket.receive_bytes()

                # 写入文件
                if temp_file:
                    temp_file.write(binary_data)

                active_uploads[file_id]["received_chunks"] += 1

                # 发送确认
                await websocket.send_json({
                    "type": "chunk",
                    "received": active_uploads[file_id]["received_chunks"]
                })

            elif message["type"] == "stop":
                if not file_id or file_id != message.get("filename"):
                    await websocket.send_json({
                        "type": "error",
                        "message": "无效的文件ID"
                    })
                    continue

                # 关闭文件
                if temp_file:
                    temp_file.close()
                    temp_file = None

                # 移动到最终位置
                upload_info = active_uploads[file_id]
                final_dir = "static/uploads/files"
                os.makedirs(final_dir, exist_ok=True)
                final_path = os.path.join(
                    final_dir, f"{file_id}.{message.get('fileType', '')}")

                try:
                    os.rename(upload_info["path"], final_path)
                    await websocket.send_json({
                        "type": "complete",
                        "filename": file_id,
                        "path": final_path
                    })
                except Exception as e:
                    config.logger.error(f"文件处理失败: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"文件处理失败: {str(e)}"
                    })

                # 清理
                if file_id in active_uploads:
                    del active_uploads[file_id]

    except WebSocketDisconnect:
        config.logger.info("WebSocket 连接断开")
    except Exception as e:
        config.logger.error(f"WebSocket 错误: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"服务器错误: {str(e)}"
            })
        except:
            pass
    finally:
        # 清理资源
        if temp_file:
            temp_file.close()
