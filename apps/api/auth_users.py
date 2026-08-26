"""Named portal users — Kevin (owner), Edwin (CPA), Nick (owner).

Passwords live in env, never in git.

  PORTAL_USERS_JSON = '[{"username":"kevin","password":"...","role":"owner",
                          "name":"Kevin Carey","email":"admin@contabia.co"}, ...]'

Backward compatible: if PORTAL_USERS_JSON is unset, PORTAL_USER + PORTAL_PASSWORD
still authenticate as a single owner (the 2026-07-24 interim login).
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Optional

_TOKEN_NS = "contabia-portal-v2"


def _token_for(username: str, password: str) -> str:
    return hashlib.sha256(f"{username}:{password}:{_TOKEN_NS}".encode()).hexdigest()


def _load_users() -> list[dict]:
    raw = os.environ.get("PORTAL_USERS_JSON", "").strip()
    users: list[dict] = []
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("PORTAL_USERS_JSON is not valid JSON") from exc
        if not isinstance(parsed, list):
            raise RuntimeError("PORTAL_USERS_JSON must be a JSON array")
        for row in parsed:
            users.append(_normalize(row))
    else:
        # Interim single-operator fallback (File 28 B2, 2026-07-24).
        user = os.environ.get("PORTAL_USER", "kevin").strip().lower()
        password = os.environ.get("PORTAL_PASSWORD", "")
        if password:
            users.append(
                _normalize(
                    {
                        "username": user,
                        "password": password,
                        "role": "owner",
                        "name": "Kevin Carey",
                        "email": "admin@contabia.co",
                    }
                )
            )
    return users


def _normalize(row: dict) -> dict:
    username = (row.get("username") or "").strip().lower()
    password = row.get("password") or ""
    role = (row.get("role") or "owner").strip().lower()
    if role not in {"owner", "accountant", "manager"}:
        raise RuntimeError(f"Unknown role '{role}' for user '{username}'")
    if not username or not password:
        raise RuntimeError("Each portal user needs username + password")
    email = (row.get("email") or f"{username}@contabia.co").strip().lower()
    name = row.get("name") or username
    aliases = {username, email, email.split("@")[0]}
    for extra in row.get("aliases") or []:
        aliases.add(str(extra).strip().lower())
    return {
        "username": username,
        "password": password,
        "role": role,
        "name": name,
        "email": email,
        "aliases": aliases,
        "token": _token_for(username, password),
        "default_entity": row.get("default_entity") or "sonata-001",
    }


USERS = _load_users()
TOKEN_INDEX = {u["token"]: u for u in USERS}


def authenticate(username: str, password: str) -> Optional[dict]:
    key = (username or "").strip().lower()
    if "@" in key:
        key = key  # full email is in aliases
    for user in USERS:
        if key in user["aliases"] and password == user["password"]:
            return user
    return None


def user_from_authorization(authorization: Optional[str]) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[len("Bearer ") :].strip()
    return TOKEN_INDEX.get(token)


def public_user(user: dict) -> dict:
    return {
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "default_entity": user["default_entity"],
    }
