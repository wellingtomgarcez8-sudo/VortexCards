from __future__ import annotations
import random
import uuid
from .models import Card, CardColor, CardKind

SPECIAL_SCORES = {
    CardKind.SKIP: 20,
    CardKind.REVERSE: 20,
    CardKind.DRAW_TWO: 25,
    CardKind.WILD: 40,
    CardKind.WILD_DRAW_FOUR: 50,
}

def make_card(kind: CardKind, color: CardColor | None = None, value: int | None = None) -> Card:
    score = value if kind == CardKind.NUMBER and value is not None else SPECIAL_SCORES.get(kind, 0)
    return Card(uuid.uuid4().hex, kind, color, value, score)

def build_standard_deck() -> list[Card]:
    cards: list[Card] = []
    for color in CardColor:
        cards.append(make_card(CardKind.NUMBER, color, 0))
        for value in range(1, 10):
            cards.extend([make_card(CardKind.NUMBER, color, value), make_card(CardKind.NUMBER, color, value)])
        for kind in (CardKind.SKIP, CardKind.REVERSE, CardKind.DRAW_TWO):
            cards.extend([make_card(kind, color), make_card(kind, color)])
    cards.extend(make_card(CardKind.WILD) for _ in range(4))
    cards.extend(make_card(CardKind.WILD_DRAW_FOUR) for _ in range(4))
    return cards

def shuffled_deck(rng: random.Random | None = None) -> list[Card]:
    rng = rng or random.Random()
    cards = build_standard_deck()
    rng.shuffle(cards)
    return cards
