from __future__ import annotations
import random
from collections import Counter
from vortexcards.game.models import CardColor, CardKind, PlayerState
from vortexcards.game.engine import GameEngine

class BotController:
    def __init__(self, difficulty: str = "normal", rng: random.Random | None = None):
        self.difficulty = difficulty
        self.rng = rng or random.Random()

    def choose(self, engine: GameEngine, player: PlayerState):
        valid = engine.valid_cards(player)
        if not valid:
            return None, None
        if self.difficulty == "beginner":
            numeric = [c for c in valid if c.kind == CardKind.NUMBER]
            card = self.rng.choice(numeric or valid)
        else:
            color_counts = Counter(c.color for c in player.hand if c.color)
            def score(card):
                s = 0
                if card.kind == CardKind.NUMBER:
                    s += 20
                if card.color:
                    s += color_counts[card.color] * 3
                if card.kind in (CardKind.SKIP, CardKind.DRAW_TWO, CardKind.WILD_DRAW_FOUR):
                    opponents = [p for p in engine.players if p.player_id != player.player_id]
                    if opponents and min(len(p.hand) for p in opponents) <= 2:
                        s += 30
                if card.kind in (CardKind.WILD, CardKind.WILD_DRAW_FOUR):
                    s -= 5
                return s
            card = max(valid, key=score)
        chosen = None
        if card.kind in (CardKind.WILD, CardKind.WILD_DRAW_FOUR):
            colors = Counter(c.color for c in player.hand if c.color)
            chosen = colors.most_common(1)[0][0] if colors else self.rng.choice(list(CardColor))
        return card, chosen
