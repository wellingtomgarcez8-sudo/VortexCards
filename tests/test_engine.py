import random
import pytest
from vortexcards.game.engine import GameEngine, RuleError
from vortexcards.game.models import PlayerState, Card, CardColor, CardKind


def engine2():
    e=GameEngine([PlayerState("a","A"),PlayerState("b","B")],random.Random(1));e.start();return e

def test_start_has_seven_cards_each():
    e=engine2();assert all(len(p.hand)>=7 for p in e.players);assert e.started

def test_numeric_matches_color_or_number():
    e=engine2();e.discard_pile=[Card("t",CardKind.NUMBER,CardColor.RED,5,5)];e.active_color=CardColor.RED
    assert e.is_playable(Card("x",CardKind.NUMBER,CardColor.RED,1,1))
    assert e.is_playable(Card("y",CardKind.NUMBER,CardColor.BLUE,5,5))
    assert not e.is_playable(Card("z",CardKind.NUMBER,CardColor.BLUE,3,3))

def test_special_is_always_playable():
    e=engine2();assert e.is_playable(Card("s",CardKind.SKIP,CardColor.GREEN,None,20))

def test_wrong_player_cannot_play():
    e=engine2();p=e.current_player;other=next(x for x in e.players if x!=p)
    with pytest.raises(RuleError):e.play_card(other.player_id,other.hand[0].card_id)

def test_public_state_hides_other_hands():
    e=engine2();s=e.public_state_for("a");assert "hand" in s;assert all("hand" not in p for p in s["players"])
