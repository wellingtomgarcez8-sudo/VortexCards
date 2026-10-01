from __future__ import annotations
import asyncio
import secrets
import uuid
from dataclasses import dataclass, field
from vortexcards.game.engine import GameEngine, RuleError
from vortexcards.game.models import PlayerState, CardColor
from .protocol import read_message, encode_message, make_message

@dataclass
class ClientSession:
    player: PlayerState
    writer: asyncio.StreamWriter
    reconnect_token: str
    seen_requests: set[str] = field(default_factory=set)

class GameServer:
    def __init__(self, host="0.0.0.0", port=27845, room_name="Sala Vórtex", max_players=6):
        self.host = host
        self.port = port
        self.room_name = room_name
        self.max_players = max(2, min(6, max_players))
        self.room_code = "VX" + secrets.token_hex(2).upper()
        self.sessions: dict[str, ClientSession] = {}
        self.engine: GameEngine | None = None
        self.server: asyncio.AbstractServer | None = None

    async def start(self):
        self.server = await asyncio.start_server(self._accept, self.host, self.port)
        sockets = self.server.sockets or []
        if sockets:
            self.port = sockets[0].getsockname()[1]
        return self

    async def close(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        for session in list(self.sessions.values()):
            session.writer.close()
        self.sessions.clear()

    async def _accept(self, reader, writer):
        player_id = None
        try:
            while True:
                msg = await read_message(reader)
                if player_id and msg["request_id"] in self.sessions[player_id].seen_requests:
                    continue
                if player_id:
                    self.sessions[player_id].seen_requests.add(msg["request_id"])
                t = msg["type"]
                p = msg["payload"]
                if t == "JOIN_ROOM":
                    if len(self.sessions) >= self.max_players:
                        await self._send(writer, "ERROR", {"message": "Sala cheia"})
                        continue
                    name = str(p.get("name", "Convidado"))[:24].strip() or "Convidado"
                    player_id = uuid.uuid4().hex
                    player = PlayerState(player_id, name)
                    token = secrets.token_urlsafe(32)
                    self.sessions[player_id] = ClientSession(player, writer, token)
                    await self._send(writer, "ROOM_STATE", self._room_state() | {"player_id": player_id, "reconnect_token": token})
                    await self._broadcast_room()
                elif not player_id:
                    await self._send(writer, "ERROR", {"message": "Entre em uma sala primeiro"})
                elif t == "PLAYER_READY":
                    self.sessions[player_id].player.ready = bool(p.get("ready", True))
                    await self._broadcast_room()
                elif t == "START_GAME":
                    if len(self.sessions) < 2:
                        raise RuleError("São necessários ao menos dois jogadores")
                    players = [s.player for s in self.sessions.values()]
                    self.engine = GameEngine(players)
                    self.engine.start()
                    await self._broadcast_game_state()
                elif t == "PLAY_CARD":
                    if not self.engine:
                        raise RuleError("Partida não iniciada")
                    chosen = CardColor(p["chosen_color"]) if p.get("chosen_color") else None
                    self.engine.play_card(player_id, str(p.get("card_id", "")), chosen)
                    await self._broadcast_game_state()
                elif t == "DRAW_CARD":
                    if not self.engine:
                        raise RuleError("Partida não iniciada")
                    self.engine.draw_for_turn(player_id)
                    await self._broadcast_game_state()
                elif t == "END_TURN":
                    if not self.engine:
                        raise RuleError("Partida não iniciada")
                    self.engine.end_turn(player_id)
                    await self._broadcast_game_state()
                elif t == "PING":
                    await self._send(writer, "PONG", {})
                elif t == "LEAVE_ROOM":
                    break
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        except Exception as exc:
            try:
                await self._send(writer, "ERROR", {"message": str(exc)})
            except Exception:
                pass
        finally:
            if player_id in self.sessions:
                self.sessions[player_id].player.connected = False
                self.sessions.pop(player_id, None)
                await self._broadcast_room()
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    def _room_state(self):
        return {
            "room_name": self.room_name,
            "room_code": self.room_code,
            "max_players": self.max_players,
            "players": [{"player_id": s.player.player_id, "name": s.player.name, "ready": s.player.ready} for s in self.sessions.values()],
        }

    async def _send(self, writer, msg_type, payload):
        writer.write(encode_message(make_message(msg_type, payload)))
        await writer.drain()

    async def _broadcast_room(self):
        payload = self._room_state()
        await asyncio.gather(*(self._send(s.writer, "ROOM_STATE", payload) for s in self.sessions.values()), return_exceptions=True)

    async def _broadcast_game_state(self):
        if not self.engine:
            return
        await asyncio.gather(*(self._send(s.writer, "GAME_STATE", self.engine.public_state_for(pid)) for pid, s in self.sessions.items()), return_exceptions=True)
