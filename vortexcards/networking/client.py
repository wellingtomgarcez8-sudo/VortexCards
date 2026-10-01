from __future__ import annotations
import asyncio
from .protocol import read_message, encode_message, make_message

class GameClient:
    def __init__(self):
        self.reader = None
        self.writer = None
        self.inbox: asyncio.Queue[dict] = asyncio.Queue()
        self._task = None

    async def connect(self, host: str, port: int, name: str):
        self.reader, self.writer = await asyncio.open_connection(host, port)
        self._task = asyncio.create_task(self._reader_loop())
        await self.send("JOIN_ROOM", {"name": name})

    async def send(self, msg_type: str, payload: dict | None = None):
        if not self.writer:
            raise ConnectionError("Cliente não conectado")
        self.writer.write(encode_message(make_message(msg_type, payload)))
        await self.writer.drain()

    async def recv(self, timeout: float | None = None):
        if timeout is None:
            return await self.inbox.get()
        return await asyncio.wait_for(self.inbox.get(), timeout)

    async def _reader_loop(self):
        try:
            while True:
                await self.inbox.put(await read_message(self.reader))
        except Exception as exc:
            await self.inbox.put(make_message("ERROR", {"message": f"Conexão encerrada: {exc}"}))

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        if self._task:
            self._task.cancel()
