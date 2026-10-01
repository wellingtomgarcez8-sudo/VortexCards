import json
from vortexcards.networking.protocol import make_message, encode_message


def test_wire_format_is_utf8_json_not_platform_binary():
    message = make_message("PLAY_CARD", {"card_id": "abc", "chosen_color": "blue"})
    frame = encode_message(message)
    payload = frame[4:].decode("utf-8")
    decoded = json.loads(payload)
    assert decoded["type"] == "PLAY_CARD"
    assert decoded["payload"]["chosen_color"] == "blue"
    assert b"pickle" not in frame.lower()
