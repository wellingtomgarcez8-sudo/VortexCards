from __future__ import annotations
import json
import struct
import uuid

PROTOCOL_VERSION = 1
MAX_PACKET = 1024 * 1024
ALLOWED_TYPES = {
    "HELLO", "JOIN_ROOM", "ROOM_STATE", "PLAYER_READY", "START_GAME",
    "PLAY_CARD", "DRAW_CARD", "END_TURN", "GAME_STATE", "PRIVATE_HAND",
    "PING", "PONG", "ERROR", "LEAVE_ROOM", "RECONNECT", "GAME_EVENT"
}

def make_message(msg_type: str, payload: dict | None = None, request_id: str | None = None) -> dict:
    if msg_type not in ALLOWED_TYPES:
        raise ValueError(f"Tipo de mensagem não suportado: {msg_type}")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "type": msg_type,
        "request_id": request_id or uuid.uuid4().hex,
        "payload": payload or {},
    }

def encode_message(message: dict) -> bytes:
    raw = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_PACKET:
        raise ValueError("Pacote excede o limite permitido")
    return struct.pack("!I", len(raw)) + raw

async def read_message(reader) -> dict:
    header = await reader.readexactly(4)
    size = struct.unpack("!I", header)[0]
    if size <= 0 or size > MAX_PACKET:
        raise ValueError("Tamanho de pacote inválido")
    raw = await reader.readexactly(size)
    message = json.loads(raw.decode("utf-8"))
    validate_message(message)
    return message

def validate_message(message: dict) -> None:
    if not isinstance(message, dict):
        raise ValueError("Mensagem inválida")
    if message.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Versão de protocolo incompatível")
    if message.get("type") not in ALLOWED_TYPES:
        raise ValueError("Tipo de mensagem inválido")
    if not isinstance(message.get("payload"), dict):
        raise ValueError("Payload inválido")
    rid = message.get("request_id")
    if not isinstance(rid, str) or not (1 <= len(rid) <= 128):
        raise ValueError("request_id inválido")
