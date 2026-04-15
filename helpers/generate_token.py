"""
helpers/generate_token.py — Generate a LiveKit room access token.

Usage:
    python helpers/generate_token.py
    python helpers/generate_token.py --room my-room --identity sir --ttl 3600
"""
import argparse
import base64
import hashlib
import hmac
import json
import time

from ayoub.config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET


def generate_token(room: str, identity: str, ttl_seconds: int = 3600) -> str:
    """Generate a signed LiveKit JWT room token."""
    now = int(time.time())

    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()

    payload = base64.urlsafe_b64encode(
        json.dumps({
            "iss": LIVEKIT_API_KEY,
            "sub": identity,
            "iat": now,
            "exp": now + ttl_seconds,
            "video": {
                "roomJoin":       True,
                "room":           room,
                "canPublish":     True,
                "canSubscribe":   True,
                "canPublishData": True,
            },
        }).encode()
    ).rstrip(b"=").decode()

    sig_input = f"{header}.{payload}".encode()
    sig = base64.urlsafe_b64encode(
        hmac.new(LIVEKIT_API_SECRET.encode(), sig_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode()

    return f"{header}.{payload}.{sig}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a LiveKit room token")
    parser.add_argument("--room",     default="ayoub-room", help="Room name (default: ayoub-room)")
    parser.add_argument("--identity", default="sir",        help="Participant identity (default: sir)")
    parser.add_argument("--ttl",      default=3600, type=int, help="Token TTL in seconds (default: 3600)")
    args = parser.parse_args()

    token = generate_token(args.room, args.identity, args.ttl)

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║           LIVEKIT ROOM TOKEN (valid 1 hour)             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  Room:     {args.room}")
    print(f"  Identity: {args.identity}")
    print(f"  Expires:  {args.ttl // 60} minutes from now")
    print()
    print("  TOKEN:")
    print(f"  {token}")
    print()
    print("  → Paste this token at: https://agents-playground.livekit.io")
    print(f"  → LiveKit URL: wss://garv-1o3sb66f.livekit.cloud")
    print()


if __name__ == "__main__":
    main()
