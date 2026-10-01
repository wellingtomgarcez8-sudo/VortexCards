from __future__ import annotations
from dataclasses import dataclass, field
import random
from .models import Card, CardColor, CardKind, PlayerState
from .deck import shuffled_deck

class RuleError(ValueError):
    pass

@dataclass
class GameEngine:
    players: list[PlayerState]
    rng: random.Random = field(default_factory=random.Random)
    draw_pile: list[Card] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)
    active_color: CardColor | None = None
    current_index: int = 0
    direction: int = 1
    started: bool = False
    winner_id: str | None = None
    sequence: int = 0
    pending_color_player_id: str | None = None
    drawn_this_turn: bool = False
    events: list[dict] = field(default_factory=list)

    def start(self, hand_size: int = 7) -> None:
        if not (2 <= len(self.players) <= 6):
            raise RuleError("A partida exige de 2 a 6 jogadores.")
        self.draw_pile = shuffled_deck(self.rng)
        self.discard_pile = []
        self.direction = 1
        self.winner_id = None
        self.sequence = 0
        self.pending_color_player_id = None
        self.drawn_this_turn = False
        for player in self.players:
            player.hand.clear()
            for _ in range(hand_size):
                player.hand.append(self._draw_one())
        first = self._draw_one()
        while first.kind in (CardKind.WILD, CardKind.WILD_DRAW_FOUR):
            self.draw_pile.insert(0, first)
            self.rng.shuffle(self.draw_pile)
            first = self._draw_one()
        self.discard_pile.append(first)
        self.active_color = first.color
        self.current_index = self.rng.randrange(len(self.players))
        self.started = True
        self._apply_initial_effect(first)
        self._emit("GAME_STARTED", {"top": first.to_dict(), "current_player_id": self.current_player.player_id})

    @property
    def current_player(self) -> PlayerState:
        return self.players[self.current_index]

    @property
    def top_card(self) -> Card:
        return self.discard_pile[-1]

    def _emit(self, event_type: str, payload: dict) -> None:
        self.sequence += 1
        self.events.append({"seq": self.sequence, "type": event_type, "payload": payload})

    def _next_index(self, steps: int = 1) -> int:
        return (self.current_index + (self.direction * steps)) % len(self.players)

    def _advance(self, steps: int = 1) -> None:
        self.current_index = self._next_index(steps)
        self.drawn_this_turn = False
        self._emit("TURN_CHANGED", {"current_player_id": self.current_player.player_id})

    def _recycle(self) -> None:
        if len(self.discard_pile) <= 1:
            raise RuleError("Não há cartas suficientes para reconstruir o baralho.")
        top = self.discard_pile.pop()
        self.draw_pile = self.discard_pile[:]
        self.discard_pile = [top]
        self.rng.shuffle(self.draw_pile)
        self._emit("DECK_RECYCLED", {})

    def _draw_one(self) -> Card:
        if not self.draw_pile:
            self._recycle()
        return self.draw_pile.pop()

    def draw_cards(self, player: PlayerState, amount: int) -> list[Card]:
        cards = [self._draw_one() for _ in range(amount)]
        player.hand.extend(cards)
        return cards

    def is_playable(self, card: Card) -> bool:
        if card.kind != CardKind.NUMBER:
            return True
        return card.color == self.active_color or (self.top_card.kind == CardKind.NUMBER and card.value == self.top_card.value)

    def valid_cards(self, player: PlayerState) -> list[Card]:
        return [c for c in player.hand if self.is_playable(c)]

    def play_card(self, player_id: str, card_id: str, chosen_color: CardColor | None = None) -> None:
        if not self.started or self.winner_id:
            raise RuleError("A partida não está ativa.")
        if self.pending_color_player_id:
            raise RuleError("Há uma escolha de cor pendente.")
        player = self.current_player
        if player.player_id != player_id:
            raise RuleError("Não é o turno deste jogador.")
        card = next((c for c in player.hand if c.card_id == card_id), None)
        if not card:
            raise RuleError("Carta não pertence à mão do jogador.")
        if not self.is_playable(card):
            raise RuleError("Jogada inválida.")
        if card.kind in (CardKind.WILD, CardKind.WILD_DRAW_FOUR) and chosen_color is None:
            raise RuleError("Escolha uma cor para esta carta.")
        player.hand.remove(card)
        self.discard_pile.append(card)
        self.active_color = chosen_color if card.kind in (CardKind.WILD, CardKind.WILD_DRAW_FOUR) else card.color
        self._emit("CARD_PLAYED", {"player_id": player_id, "card": card.to_dict(), "active_color": self.active_color.value})
        steps = 1
        if card.kind == CardKind.SKIP:
            steps = 2
            self._emit("SKIP", {"skipped_player_id": self.players[self._next_index(1)].player_id})
        elif card.kind == CardKind.REVERSE:
            if len(self.players) == 2:
                steps = 2
            else:
                self.direction *= -1
                steps = 1
            self._emit("REVERSE", {"direction": self.direction})
        elif card.kind == CardKind.DRAW_TWO:
            target = self.players[self._next_index(1)]
            self.draw_cards(target, 2)
            steps = 2
            self._emit("DRAW_PENALTY", {"player_id": target.player_id, "amount": 2})
        elif card.kind == CardKind.WILD_DRAW_FOUR:
            target = self.players[self._next_index(1)]
            self.draw_cards(target, 4)
            steps = 2
            self._emit("DRAW_PENALTY", {"player_id": target.player_id, "amount": 4})
        if not player.hand:
            self.winner_id = player.player_id
            gained = sum(c.score for p in self.players if p.player_id != player.player_id for c in p.hand)
            player.score += gained
            self._emit("GAME_OVER", {"winner_id": player.player_id, "round_score": gained, "total_score": player.score})
            return
        if len(player.hand) == 1:
            self._emit("LAST_CARD", {"player_id": player.player_id})
        self._advance(steps)

    def draw_for_turn(self, player_id: str) -> Card:
        if self.current_player.player_id != player_id:
            raise RuleError("Não é o turno deste jogador.")
        if self.drawn_this_turn:
            raise RuleError("O jogador já comprou neste turno.")
        card = self._draw_one()
        self.current_player.hand.append(card)
        self.drawn_this_turn = True
        self._emit("CARD_DRAWN", {"player_id": player_id, "count": 1})
        return card

    def end_turn(self, player_id: str) -> None:
        if self.current_player.player_id != player_id:
            raise RuleError("Não é o turno deste jogador.")
        if not self.drawn_this_turn and self.valid_cards(self.current_player):
            raise RuleError("Existe uma jogada válida; compre apenas se necessário.")
        self._advance(1)

    def _apply_initial_effect(self, card: Card) -> None:
        if card.kind == CardKind.SKIP:
            self.current_index = self._next_index(1)
        elif card.kind == CardKind.REVERSE:
            if len(self.players) == 2:
                self.current_index = self._next_index(1)
            else:
                self.direction = -1
        elif card.kind == CardKind.DRAW_TWO:
            target = self.current_player
            self.draw_cards(target, 2)
            self.current_index = self._next_index(1)

    def public_state_for(self, player_id: str) -> dict:
        own = next(p for p in self.players if p.player_id == player_id)
        return {
            "sequence": self.sequence,
            "started": self.started,
            "winner_id": self.winner_id,
            "active_color": self.active_color.value if self.active_color else None,
            "direction": self.direction,
            "current_player_id": self.current_player.player_id if self.started else None,
            "top_card": self.top_card.to_dict() if self.discard_pile else None,
            "players": [{
                "player_id": p.player_id,
                "name": p.name,
                "card_count": len(p.hand),
                "connected": p.connected,
                "ready": p.ready,
                "is_bot": p.is_bot,
                "score": p.score,
            } for p in self.players],
            "hand": [c.to_dict() for c in own.hand],
        }
