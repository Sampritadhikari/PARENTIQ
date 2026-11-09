import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # child_id -> set of active parent WebSocket connections
        self.parent_connections: Dict[str, Set[WebSocket]] = {}
        # device_id -> active child device WebSocket connection
        self.device_connections: Dict[str, WebSocket] = {}

    async def connect_parent(self, child_id: str, websocket: WebSocket):
        await websocket.accept()
        if child_id not in self.parent_connections:
            self.parent_connections[child_id] = set()
        self.parent_connections[child_id].add(websocket)

    def disconnect_parent(self, child_id: str, websocket: WebSocket):
        if child_id in self.parent_connections:
            self.parent_connections[child_id].discard(websocket)
            if not self.parent_connections[child_id]:
                del self.parent_connections[child_id]

    async def connect_device(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.device_connections[device_id] = websocket

    def disconnect_device(self, device_id: str):
        if device_id in self.device_connections:
            del self.device_connections[device_id]

    async def send_to_device(self, device_id: str, message: dict) -> bool:
        ws = self.device_connections.get(device_id)
        if ws:
            try:
                await ws.send_text(json.dumps(message))
                return True
            except Exception:
                self.disconnect_device(device_id)
        return False

    async def broadcast_to_parents(self, child_id: str, message: dict):
        connections = self.parent_connections.get(child_id, set())
        dead_connections = set()
        for ws in connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead_connections.add(ws)
        for ws in dead_connections:
            connections.discard(ws)


ws_manager = WebSocketManager()

