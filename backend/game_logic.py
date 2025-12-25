import random
from typing import List, Dict, Optional

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["♠", "♥", "♦", "♣"]


def build_deck():
    return [f"{rank}{suit}" for rank in RANKS for suit in SUITS]


def card_rank(card: str) -> str:
    return card[:-1]


class BluffGame:
    def __init__(self, player_ids: List[str]):
        self.players = player_ids[:]
        self.current_turn_index = 0

        self.player_hands: Dict[str, List[str]] = {}
        self.pile: List[str] = []

        self.claim_rank: Optional[str] = None
        self.claim_starter: Optional[str] = None
        self.last_played: Optional[Dict] = None

        self.consecutive_passes = 0
        self.game_over = False
        self.pending_winner: Optional[str] = None


        self._deal_cards()
        self._debug_state("GAME INIT")

    # -------------------------
    # SETUP
    # -------------------------

    def _deal_cards(self):
        deck = build_deck()
        random.shuffle(deck)

        if len(self.players) == 3:
            deck.pop()

        self.player_hands = {pid: [] for pid in self.players}

        for i, card in enumerate(deck):
            self.player_hands[self.players[i % len(self.players)]].append(card)

    # -------------------------
    # DEBUG
    # -------------------------

    def _debug_state(self, label: str):
        print("\n========== DEBUG:", label, "==========")
        print("Turn:", self.current_player())
        print("Claim:", self.claim_rank)
        print("Claim Starter:", self.claim_starter)
        print("Pile:", self.pile)
        print("Last Played:", self.last_played)
        print("Hands:", {p: len(self.player_hands[p]) for p in self.players})
        print("Passes:", self.consecutive_passes)
        print("====================================\n")

    # -------------------------
    # HELPERS
    # -------------------------

    def current_player(self) -> str:
        return self.players[self.current_turn_index]

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)

    def _validate_turn(self, player_id: str):
        if self.game_over:
            raise ValueError("Game is over")
        if player_id != self.current_player():
            raise ValueError("Not your turn")

    # -------------------------
    # ACTIONS
    # -------------------------

    def play_cards(self, player_id: str, cards: List[str], claim_rank: Optional[str] = None):
        self._validate_turn(player_id)

        if not cards or len(cards) > 4:
            raise ValueError("Must play 1 to 4 cards")

        for c in cards:
            if c not in self.player_hands[player_id]:
                raise ValueError("Card not in hand")

        # new claim ONLY if pile is empty
        if self.claim_rank is None:
            if claim_rank not in RANKS:
                raise ValueError("Invalid claim")
            self.claim_rank = claim_rank
            self.claim_starter = player_id
            self.consecutive_passes = 0
        else:
            if claim_rank is not None:
                raise ValueError("Claim already set")

        for c in cards:
            self.player_hands[player_id].remove(c)
            self.pile.append(c)

        self.last_played = {
            "player": player_id,
            "cards": cards[:],
            "emptied_hand": not self.player_hands[player_id]
        }

        if not self.player_hands[player_id]:
            self.pending_winner = player_id


        self.consecutive_passes = 0

        self._debug_state(f"PLAY by {player_id}")

        # if not self.player_hands[player_id]:
        #     self.game_over = True
        #     return {"event": "game_over", "winner": player_id}

        self.next_turn()

        return {
            "event": "cards_played",
            "by": player_id,
            "count": len(cards),
            "claim": self.claim_rank,
            "cards": cards[:] 
        }

    
    def pass_turn(self, player_id: str):
        self._validate_turn(player_id)

        self.consecutive_passes += 1
        self._debug_state(f"PASS by {player_id}")

        # Everyone passed
        if self.consecutive_passes >= len(self.players):
            if not self.last_played or self.claim_rank is None:
                raise ValueError("Invalid state: pass without active claim")

            last_player = self.last_played["player"]
            # winner_candidate = (
            #     last_player if self.last_played.get("emptied_hand") else None
            # )

            # Reset round state
            self.pile.clear()
            self.claim_rank = None
            self.last_played = None
            self.consecutive_passes = 0
            self.claim_starter = None

            # LAST CARD PLAYER STARTS NEXT ROUND
            self.current_turn_index = self.players.index(last_player)

            self._debug_state("PILE DUMPED")

            # Game over if last player had no cards
            if self.pending_winner:
                self.game_over = True
                winner = self.pending_winner
                self.pending_winner = None
                return {
                    "event": "game_over",
                    "winner": winner
                }
                

            return {
                "event": "pile_dumped",
                "next_player": self.current_player()
            }

        # Normal pass
        self.next_turn()
        return {"event": "pass", "by": player_id}


    

    def call_doubt(self, player_id: str):
        self._validate_turn(player_id)

        if not self.last_played:
            raise ValueError("Nothing to doubt")

        last_player = self.last_played["player"]
        last_cards = self.last_played["cards"]
        emptied_hand = self.last_played["emptied_hand"]

        # Check only last play against claim
        truthful = all(card_rank(c) == self.claim_rank for c in last_cards)

        if truthful:
            # Doubter loses
            self.player_hands[player_id].extend(self.pile)
            next_player = last_player
            loser = player_id
            result = "truth"
        else:
            # Liar loses
            self.player_hands[last_player].extend(self.pile)
            next_player = player_id
            loser = last_player
            result = "lie"

            # Cancel win if liar was pending winner
            if self.pending_winner == last_player:
                self.pending_winner = None

        # Clear round state
        self.pile.clear()
        self.claim_rank = None
        self.last_played = None
        self.consecutive_passes = 0
        self.claim_starter = None

        self.current_turn_index = self.players.index(next_player)

        self._debug_state(f"DOUBT by {player_id}")

        # FINAL WIN CHECK (global)
        if self.pending_winner:
            self.game_over = True
            winner = self.pending_winner
            self.pending_winner = None
            return {
                "event": "game_over",
                "winner": winner
            }
            

        return {
            "event": "doubt_result",
            "result": result,
            "loser": loser,
            "next_player": next_player,
            "cards": last_cards
        }
    
    


    # -------------------------
    # STATE
    # -------------------------

    def get_public_state(self):
        return {
            "current_turn": self.current_player(),
            "claim": self.claim_rank,
            "pile_count": len(self.pile),
            "last_play_count": len(self.last_played["cards"]) if self.last_played else 0,
            "players": {
                pid: len(self.player_hands[pid]) for pid in self.players
            }
        }

    def get_player_hand(self, player_id: str):
        return self.player_hands.get(player_id, [])
