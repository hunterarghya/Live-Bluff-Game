import os
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.socket_manager import manager
from backend.routes_auth import router as auth_router
from backend.routes_rooms import router as room_router
from backend.routes_rooms import remove_user_from_room
from backend.auth import decode_token
from backend.db import rooms_col
from backend.game_logic import BluffGame
from backend.state import active_games


app = FastAPI()

# -------------------- MIDDLEWARE --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- ROUTERS --------------------
app.include_router(auth_router)
app.include_router(room_router)

# -------------------- FRONTEND --------------------
frontend_path = os.path.join(os.getcwd(), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

def build_ui_players(room, game=None):
    players = []
    for p in room["players"]:
        players.append({
            "id": p["id"],
            "name": p["name"],
            "cards": len(game.player_hands[p["id"]]) if game else None
        })
    return players


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# -------------------- WEBSOCKET --------------------
@app.websocket("/ws/{room_code}/{token}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, token: str):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    user_id = payload["sub"]
    user_name = payload.get("name", "Unknown")

    room = rooms_col.find_one({
        "room_code": room_code,
        "players.id": user_id
    })

    if not room:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, room_code, user_id)
    print(f"[WS] CONNECT | {user_name} -> {room_code}")

    try:
        # ================= JOIN =================
        await manager.broadcast(room_code, {
            "type": "chat",
            "user": "System",
            "message": f"{user_name} joined the room."
        })

        # Send room state
        game = active_games.get(room_code)

        await manager.broadcast(room_code, {
            "type": "room_update",
            "players": build_ui_players(room, game),
            "current_turn": game.current_player() if game else None,
            "game_started": bool(game)
        })

        # ================= LOOP =================
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            msg_type = message.get("type")

            print(f"[WS] {room_code} | {user_name} -> {msg_type}")

            # ---------- CHAT ----------
            if msg_type == "chat":
                await manager.broadcast(room_code, {
                    "type": "chat",
                    "user": user_name,
                    "message": message.get("message", "")
                })

            # ---------- WEBRTC ----------
            elif msg_type in {"offer", "answer", "candidate", "vc_request"}:
                await manager.broadcast(room_code, message)

            # ---------- START GAME ----------
            elif msg_type == "start_game":
                game = active_games.get(room_code)
                if game and not game.game_over:
                    await manager.send_to_user(room_code, user_id, {
                        "type": "error",
                        "message": "Game already running"
                    })
                    continue

                room = rooms_col.find_one({"room_code": room_code})
                if not room:
                    continue

                player_ids = [p["id"] for p in room["players"]]

                if len(player_ids) < 2:
                    await manager.send_to_user(room_code, user_id, {
                        "type": "error",
                        "message": "At least 2 players required"
                    })
                    continue

                from backend.state import start_game
                game = start_game(room_code, player_ids)

                print(f"[GAME] Started in {room_code} with players {player_ids}")

                # Public game state
                await manager.broadcast(room_code, {
                    "type": "game_state",
                    **game.get_public_state()
                })

                # Room update
                await manager.broadcast(room_code, {
                    "type": "room_update",
                    "players": build_ui_players(room, game),
                    "current_turn": game.current_player(),
                    "game_started": True
                })

                # Private hands
                for pid in game.players:
                    await manager.send_to_user(room_code, pid, {
                        "type": "your_hand",
                        "hand": game.get_player_hand(pid)
                    })

            # ---------- GAME ACTIONS ----------
            elif msg_type in {"play", "pass", "doubt"}:
                game = active_games.get(room_code)
                if not game:
                    continue

                try:
                    if msg_type == "play":
                        result = game.play_cards(
                            user_id,
                            message.get("cards", []),
                            message.get("claim")
                        )
                    elif msg_type == "pass":
                        result = game.pass_turn(user_id)
                    else:
                        result = game.call_doubt(user_id)

                except ValueError as e:
                    await manager.send_to_user(room_code, user_id, {
                        "type": "error",
                        "message": str(e)
                    })
                    continue

                # Game event (pass / play / doubt result)
                await manager.broadcast(room_code, {
                    "type": "game_event",
                    **result
                })

                # Public game state
                await manager.broadcast(room_code, {
                    "type": "game_state",
                    **game.get_public_state()
                })

                # REFRESH ROOM STATE BEFORE BROADCAST
                room = rooms_col.find_one({"room_code": room_code})
                if not room:
                    continue

                # Room update
                await manager.broadcast(room_code, {
                    "type": "room_update",
                    "players": build_ui_players(room, game),
                    "current_turn": game.current_player(),
                    "game_started": True
                })

                # Sync ALL hands
                for pid in game.players:
                    await manager.send_to_user(room_code, pid, {
                        "type": "your_hand",
                        "hand": game.get_player_hand(pid)
                    })

            # ---------- UNKNOWN ----------
            else:
                await manager.send_to_user(room_code, user_id, {
                    "type": "error",
                    "message": "Unknown message type"
                })

    # ================= DISCONNECT =================
    except WebSocketDisconnect:
        print(f"[WS] DISCONNECT | {user_name}")
        manager.disconnect(room_code, user_id, websocket)
        remove_user_from_room(room_code, user_id)

        game = active_games.get(room_code)
        if game and user_id in game.players:
            from backend.state import end_game
            end_game(room_code)

            await manager.broadcast(room_code, {
                "type": "chat",
                "user": "System",
                "message": "Game ended because a player left."
            })
