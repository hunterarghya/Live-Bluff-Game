from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        # room_code -> user_id -> websocket
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_code: str, user_id: str):
        await websocket.accept()

        if room_code not in self.active_connections:
            self.active_connections[room_code] = {}

        # enforce 1 connection per user per room
        old_ws = self.active_connections[room_code].get(user_id)
        if old_ws and old_ws is not websocket:
            try:
                await old_ws.close(code=1000)
            except Exception:
                pass  # socket may already be dead

        self.active_connections[room_code][user_id] = websocket

        print(f"[CONNECT] room={room_code} user={user_id} ws={id(websocket)}")

    def disconnect(self, room_code: str, user_id: str, websocket: WebSocket):
        room = self.active_connections.get(room_code)
        if not room:
            return

        # only remove if THIS websocket is the active one
        if room.get(user_id) is websocket:
            room.pop(user_id, None)

            if not room:
                self.active_connections.pop(room_code, None)

            print(f"[DISCONNECT] room={room_code} user={user_id} ws={id(websocket)}")

    async def broadcast(self, room_code: str, message: dict):
        room = self.active_connections.get(room_code, {})
        for ws in list(room.values()):
            try:
                await ws.send_json(message)
            except Exception:
                pass

    async def send_to_user(self, room_code: str, user_id: str, message: dict):
        ws = self.active_connections.get(room_code, {}).get(user_id)
        if ws:
            try:
                print(f"[SEND] to={user_id} ws={id(ws)} event={message.get('event')}")
                await ws.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()
