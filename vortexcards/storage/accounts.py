from __future__ import annotations
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .database import connect

_hasher = PasswordHasher()

def register(username: str, password: str) -> None:
    username = username.strip()
    if not (3 <= len(username) <= 24):
        raise ValueError("Nome de usuário deve ter entre 3 e 24 caracteres")
    if len(password) < 8:
        raise ValueError("Senha deve ter ao menos 8 caracteres")
    with connect() as db:
        db.execute("INSERT INTO accounts(username,password_hash) VALUES(?,?)", (username, _hasher.hash(password)))
        db.execute("INSERT OR IGNORE INTO stats(username) VALUES(?)", (username,))

def authenticate(username: str, password: str) -> bool:
    with connect() as db:
        row = db.execute("SELECT password_hash FROM accounts WHERE username=?", (username.strip(),)).fetchone()
    if not row:
        return False
    try:
        return _hasher.verify(row[0], password)
    except VerifyMismatchError:
        return False
