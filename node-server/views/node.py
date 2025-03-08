from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from utils.node import get_metrics_data
from typing import List

node = APIRouter(prefix="/node")


# 存储活跃的WebSocket连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_metrics(self, websocket: WebSocket):
        while True:
            try:
                metrics = get_metrics_data()
                await websocket.send_json(metrics)
                await asyncio.sleep(0.5)  # 每0.5秒发送一次数据
            except Exception as e:
                print(f"发送数据错误: {e}")
                break


manager = ConnectionManager()


@node.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.send_metrics(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(websocket)
