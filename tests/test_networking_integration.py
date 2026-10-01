import asyncio
import pytest
from vortexcards.networking.server import GameServer
from vortexcards.networking.client import GameClient


@pytest.mark.asyncio
async def test_two_clients_share_same_authoritative_room():
    server = await GameServer(host="127.0.0.1", port=0, room_name="Teste", max_players=6).start()
    c1, c2 = GameClient(), GameClient()
    try:
        await c1.connect("127.0.0.1", server.port, "WindowsPlayer")
        await c2.connect("127.0.0.1", server.port, "LinuxPlayer")

        states1, states2 = [], []
        for _ in range(3):
            states1.append(await c1.recv(1))
            states2.append(await c2.recv(1))
            if any(m["type"] == "ROOM_STATE" and len(m["payload"].get("players", [])) == 2 for m in states1) and any(m["type"] == "ROOM_STATE" and len(m["payload"].get("players", [])) == 2 for m in states2):
                break

        s1 = next(m for m in reversed(states1) if m["type"] == "ROOM_STATE" and len(m["payload"].get("players", [])) == 2)
        s2 = next(m for m in reversed(states2) if m["type"] == "ROOM_STATE" and len(m["payload"].get("players", [])) == 2)
        assert s1["payload"]["room_code"] == s2["payload"]["room_code"]
        assert {p["name"] for p in s1["payload"]["players"]} == {"WindowsPlayer", "LinuxPlayer"}
    finally:
        await c1.close()
        await c2.close()
        await server.close()


@pytest.mark.asyncio
async def test_private_hands_are_not_broadcast_to_other_players():
    server = await GameServer(host="127.0.0.1", port=0).start()
    c1, c2 = GameClient(), GameClient()
    try:
        await c1.connect("127.0.0.1", server.port, "A")
        await c2.connect("127.0.0.1", server.port, "B")
        host_state = None
        for _ in range(4):
            msg = await c1.recv(1)
            if msg["type"] == "ROOM_STATE" and msg["payload"].get("host_player_id"):
                host_state = msg
        assert host_state is not None
        await c1.send("START_GAME", {})
        game1 = await _next_type(c1, "GAME_STATE")
        game2 = await _next_type(c2, "GAME_STATE")
        assert "hand" in game1["payload"]
        assert "hand" in game2["payload"]
        assert all("hand" not in p for p in game1["payload"]["players"])
        assert all("hand" not in p for p in game2["payload"]["players"])
    finally:
        await c1.close()
        await c2.close()
        await server.close()


async def _next_type(client, wanted):
    for _ in range(10):
        msg = await client.recv(1)
        if msg["type"] == wanted:
            return msg
    raise AssertionError(f"Mensagem {wanted} não recebida")
