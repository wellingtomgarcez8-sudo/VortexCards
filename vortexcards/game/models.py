from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

class CardColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"

class CardKind(str, Enum):
    NUMBER = "number"
    SKIP = "skip"
    REVERSE = "reverse"
    DRAW_TWO = "draw_two"
    WILD = "wild"
    WILD_DRAW_FOUR = "wild_draw_four"

@dataclass(slots=True)
class Card:
    card_id: str
    kind: CardKind
    color: Optional[CardColor] = None
    value: Optional[int] = None
    score: int = 0

    @property
    def display_name(self) -> str:
        if self.kind == CardKind.NUMBER:
            return str(self.value)
        return {
            CardKind.SKIP: "Bloqueio",
            CardKind.REVERSE: "Inversão",
            CardKind.DRAW_TWO: "+2",
            CardKind.WILD: "Vórtice Cromático",
            CardKind.WILD_DRAW_FOUR: "Colapso Vórtice",
        }[self.kind]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["kind"] = self.kind.value
        data["color"] = self.color.value if self.color else None
        return data

    @staticmethod
    def from_dict(data: dict) -> "Card":
        return Card(
            card_id=data["card_id"],
            kind=CardKind(data["kind"]),
            color=CardColor(data["color"]) if data.get("color") else None,
            value=data.get("value"),
            score=int(data.get("score", 0)),
        )

@dataclass
class PlayerState:
    player_id: str
    name: str
    hand: list[Card] = field(default_factory=list)
    connected: bool = True
    ready: bool = False
    is_bot: bool = False
    score: int = 0

@dataclass
class PublicPlayer:
    player_id: str
    name: str
    card_count: int
    connected: bool
    ready: bool
    is_bot: bool
    score: int
