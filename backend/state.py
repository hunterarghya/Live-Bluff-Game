from backend.game_logic import BluffGame

active_games = {}  # room_code -> BluffGame


def start_game(room_code: str, player_ids: list[str]) -> BluffGame:
    game = BluffGame(player_ids)
    active_games[room_code] = game
    return game


def end_game(room_code: str):
    active_games.pop(room_code, None)
