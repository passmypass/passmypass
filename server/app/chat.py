"""
Ephemeral E2E encrypted chat rooms.

Rooms live in memory only - no database, no persistence.
Server relays ciphertext between two peers; it never sees plaintext.
"""
import asyncio
import logging
import secrets
import time
from dataclasses import dataclass, field
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.websockets import WebSocketState
from app.database import async_session
from app import statistics

logger = logging.getLogger("passmypass")

ROOM_EXPIRY_SECONDS = 600  # 10 minutes
MAX_ROOMS = 1000
CLEANUP_INTERVAL_SECONDS = 60

# Close codes
CLOSE_PEER_LEFT = 4001
CLOSE_ROOM_FULL = 4003
CLOSE_ROOM_NOT_FOUND = 4004
CLOSE_ROOM_EXPIRED = 4008


@dataclass
class Room:
    room_id: str
    created_at: float
    clients: list[WebSocket] = field(default_factory=list)
    max_participants: int = 2

    @property
    def is_full(self) -> bool:
        return len(self.clients) >= self.max_participants

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) >= ROOM_EXPIRY_SECONDS


# In-memory room storage
rooms: dict[str, Room] = {}

router = APIRouter(prefix="/api/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/rooms", status_code=201)
@limiter.limit("10/minute")
async def create_room(request: Request):
    """Create a new ephemeral chat room."""
    if len(rooms) >= MAX_ROOMS:
        logger.warning("Room creation rejected: max rooms reached")
        return {"detail": "Service at capacity. Try again later."}, 503

    room_id = secrets.token_urlsafe(16)
    rooms[room_id] = Room(room_id=room_id, created_at=time.time())

    # Track chat room creation statistic
    try:
        async with async_session() as db:
            await statistics.track_chat_room_creation(db)
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to track chat room creation stat: {type(e).__name__}")

    logger.info(f"Chat room created: {room_id[:8]}...")
    return {"room_id": room_id}


@router.websocket("/rooms/{room_id}/ws")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for chat room communication."""
    room = rooms.get(room_id)

    # Validate room
    if room is None:
        await websocket.accept()
        await websocket.close(code=CLOSE_ROOM_NOT_FOUND, reason="Room not found")
        return

    if room.is_expired:
        # Clean up expired room
        rooms.pop(room_id, None)
        await websocket.accept()
        await websocket.close(code=CLOSE_ROOM_EXPIRED, reason="Room expired")
        return

    if room.is_full:
        await websocket.accept()
        await websocket.close(code=CLOSE_ROOM_FULL, reason="Room full")
        return

    # Accept connection
    await websocket.accept()
    room.clients.append(websocket)
    logger.info(f"Peer joined room {room_id[:8]}... ({len(room.clients)}/{room.max_participants})")

    # Notify all clients that a peer is present
    # - Existing peers learn someone new joined
    # - The new joiner learns there's already a peer in the room
    if len(room.clients) > 1:
        for client in room.clients:
            try:
                await client.send_json({"type": "system", "event": "peer_joined"})
            except Exception:
                pass

    try:
        while True:
            # Check expiry on each message
            if room.is_expired:
                await _expire_room(room_id)
                return

            data = await websocket.receive_json()

            # Validate message format
            msg_type = data.get("type")
            if msg_type not in ("message", "typing"):
                continue

            # Relay to other clients
            relayed = False
            for client in room.clients:
                if client != websocket and client.client_state == WebSocketState.CONNECTED:
                    try:
                        await client.send_json(data)
                        relayed = True
                    except Exception:
                        pass

            # Track relayed messages (only actual messages, not typing indicators)
            if relayed and msg_type == "message":
                try:
                    async with async_session() as db:
                        await statistics.track_chat_message_relayed(db)
                        await db.commit()
                except Exception:
                    pass  # Don't let stats failures affect chat

    except WebSocketDisconnect:
        logger.info(f"Peer disconnected from room {room_id[:8]}...")
    except Exception as e:
        logger.error(f"WebSocket error in room {room_id[:8]}...: {type(e).__name__}")
    finally:
        # Remove this client
        if websocket in room.clients:
            room.clients.remove(websocket)

        # Notify remaining peers and destroy room
        await _destroy_room(room_id, CLOSE_PEER_LEFT, "Peer disconnected")


async def _expire_room(room_id: str):
    """Expire a room and notify all clients."""
    room = rooms.pop(room_id, None)
    if room is None:
        return

    for client in room.clients:
        try:
            if client.client_state == WebSocketState.CONNECTED:
                await client.send_json({"type": "system", "event": "room_expired"})
                await client.close(code=CLOSE_ROOM_EXPIRED, reason="Room expired")
        except Exception:
            pass

    logger.info(f"Room expired: {room_id[:8]}...")


async def _destroy_room(room_id: str, code: int, reason: str):
    """Destroy a room and close all remaining connections."""
    room = rooms.pop(room_id, None)
    if room is None:
        return

    for client in room.clients:
        try:
            if client.client_state == WebSocketState.CONNECTED:
                await client.send_json({"type": "system", "event": "peer_left"})
                await client.close(code=code, reason=reason)
        except Exception:
            pass

    logger.info(f"Room destroyed: {room_id[:8]}...")


async def cleanup_expired_rooms():
    """Background task to remove expired rooms."""
    while True:
        try:
            expired_ids = [
                rid for rid, room in rooms.items() if room.is_expired
            ]
            for rid in expired_ids:
                await _expire_room(rid)
            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired chat rooms")
        except Exception as e:
            logger.error(f"Chat cleanup error: {type(e).__name__}")

        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
