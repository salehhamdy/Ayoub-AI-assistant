"""
helpers/dispatch_agent.py — Explicitly dispatch Ayoub to a LiveKit room.

Run this AFTER the user is connected to the playground room.
It calls AgentDispatchService.create_dispatch() to send the agent into that room.

Usage:
    python helpers/dispatch_agent.py                        # dispatches to ayoub-room
    python helpers/dispatch_agent.py --room my-room         # dispatches to any room
    python helpers/dispatch_agent.py --room ayoub-room --agent ayoub

How it works (LiveKit explicit dispatch):
    1. ayoub-voice runs  → registers worker with agent_name="ayoub"
    2. User joins room   → playground shows "Waiting for agent audio track..."
    3. Run this script   → LiveKit dispatches the agent into the room immediately
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

LIVEKIT_URL        = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")


async def dispatch_agent(room: str, agent_name: str) -> None:
    try:
        from livekit import api
    except ImportError:
        print("ERROR: 'livekit' not installed. Run: pip install livekit")
        sys.exit(1)

    print(f"\n[dispatch] Connecting to {LIVEKIT_URL}")
    print(f"[dispatch] Dispatching agent '{agent_name or '(implicit)'}' → room '{room}'")

    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )

    try:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room,
                metadata='{"user": "sir"}',
            )
        )
        print(f"[dispatch] ✅ Dispatch created: {dispatch.dispatch_id}")
        print(f"[dispatch] Agent should now join room '{room}' and say hello.")

        # List all active dispatches in the room
        dispatches = await lkapi.agent_dispatch.list_dispatch(room_name=room)
        print(f"[dispatch] Active dispatches in '{room}': {len(dispatches)}")

    except Exception as e:
        print(f"[dispatch] ❌ Error: {e}")
        print("Make sure ayoub-voice is running and the room exists.")
    finally:
        await lkapi.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch Ayoub to a LiveKit room")
    parser.add_argument("--room",  default="ayoub-room", help="Room name (default: ayoub-room)")
    parser.add_argument("--agent", default="ayoub",      help="Agent name (default: ayoub)")
    args = parser.parse_args()

    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        print("ERROR: Missing LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET in .env")
        sys.exit(1)

    asyncio.run(dispatch_agent(args.room, args.agent))


if __name__ == "__main__":
    main()
