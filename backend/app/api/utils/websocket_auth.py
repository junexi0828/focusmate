"""WebSocket authentication helpers."""

from fastapi import WebSocket


def _parse_subprotocol_token(header_value: str) -> str | None:
    parts = [part.strip() for part in header_value.split(",") if part.strip()]
    if not parts:
        return None

    for idx, part in enumerate(parts):
        if part.lower() in ("access_token", "bearer", "token"):
            if idx + 1 < len(parts):
                return parts[idx + 1]

    for part in parts:
        if part.count(".") >= 2:
            return part

    return None


def extract_ws_token(websocket: WebSocket, token_param: str | None) -> str | None:
    """Extract JWT token from WebSocket query, headers, or subprotocol."""
    if token_param:
        return token_param

    auth_header = websocket.headers.get("authorization")
    if auth_header:
        scheme, _, value = auth_header.partition(" ")
        if scheme.lower() == "bearer" and value:
            return value
        if not value and scheme:
            return scheme

    protocol_header = websocket.headers.get("sec-websocket-protocol", "")
    return _parse_subprotocol_token(protocol_header) if protocol_header else None
