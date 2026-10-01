from __future__ import annotations
from .database import connect


def record_match(username: str, mode: str, won: bool, score: int, play_seconds: int = 0) -> None:
    username = username.strip()
    result = "win" if won else "loss"
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO stats(username) VALUES(?)", (username,))
        db.execute(
            "UPDATE stats SET games=games+1,wins=wins+?,losses=losses+?,play_seconds=play_seconds+? WHERE username=?",
            (1 if won else 0, 0 if won else 1, max(0, int(play_seconds)), username),
        )
        db.execute(
            "INSERT INTO history(username,mode,result,score) VALUES(?,?,?,?)",
            (username, mode, result, int(score)),
        )


def get_stats(username: str) -> dict:
    with connect() as db:
        row = db.execute("SELECT games,wins,losses,play_seconds FROM stats WHERE username=?", (username.strip(),)).fetchone()
    if not row:
        return {"games": 0, "wins": 0, "losses": 0, "play_seconds": 0, "win_rate": 0.0}
    games, wins, losses, seconds = map(int, row)
    return {
        "games": games,
        "wins": wins,
        "losses": losses,
        "play_seconds": seconds,
        "win_rate": (wins / games * 100.0) if games else 0.0,
    }


def recent_history(username: str, limit: int = 20) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            "SELECT played_at,mode,result,score FROM history WHERE username=? ORDER BY id DESC LIMIT ?",
            (username.strip(), max(1, min(100, int(limit)))),
        ).fetchall()
    return [{"played_at": r[0], "mode": r[1], "result": r[2], "score": r[3]} for r in rows]
