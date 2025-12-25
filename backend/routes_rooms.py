from fastapi import APIRouter, HTTPException, Depends
from backend.db import rooms_col
from backend.deps import get_current_user
from backend.state import active_games
import secrets
import string
from datetime import datetime


# ------------------ HELPERS ------------------
def remove_user_from_room(room_code: str, user_id: str):
    room = rooms_col.find_one({"room_code": room_code})
    if not room:
        return

    rooms_col.update_one(
        {"room_code": room_code},
        {"$pull": {"players": {"id": user_id}}}
    )

    updated = rooms_col.find_one({"room_code": room_code})
    if updated and len(updated["players"]) == 0:
        rooms_col.delete_one({"room_code": room_code})


# ------------------ ROUTER ------------------
router = APIRouter(prefix="/rooms", tags=["rooms"])


def generate_room_code():
    return ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(6)
    )


@router.post("/create")
def create_room(current_user: dict = Depends(get_current_user)):
    code = generate_room_code()
    room = {
        "room_code": code,
        "creator_id": current_user["sub"],
        "players": [{
            "id": current_user["sub"],
            "name": current_user["name"]
        }],
        "game_started": False,
        "created_at": datetime.utcnow()
    }
    rooms_col.insert_one(room)
    return {"room_code": code}


@router.get("/join/{code}")
def join_room(code: str, current_user: dict = Depends(get_current_user)):
    room = rooms_col.find_one({"room_code": code})
    if not room:
        raise HTTPException(404, "Room not found")

    if len(room["players"]) >= 4:
        raise HTTPException(400, "Room is full")

    if not any(p["id"] == current_user["sub"] for p in room["players"]):
        rooms_col.update_one(
            {"room_code": code},
            {"$push": {"players": {
                "id": current_user["sub"],
                "name": current_user["name"]
            }}}
        )

    return {"status": "joined", "room_code": code}


@router.get("/{code}")
def get_room(code: str, current_user: dict = Depends(get_current_user)):
    room = rooms_col.find_one({"room_code": code})
    if not room:
        raise HTTPException(404, "Room not found")

    return {
        "room_code": room["room_code"],
        "players": room["players"]
    }


@router.get("/{room_code}/hand")
async def get_hand(room_code: str, current_user: dict = Depends(get_current_user)):
    game = active_games.get(room_code)
    if not game:
        raise HTTPException(404, "Game not found")

    return {
        "hand": game.player_hands.get(current_user["sub"], []),
        "others": {
            p: len(cards)
            for p, cards in game.player_hands.items()
            if p != current_user["sub"]
        }
    }
