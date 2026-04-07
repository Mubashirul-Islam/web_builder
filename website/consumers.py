"""
WebSocket consumer for real-time lock event broadcasting.

Each client (viewer or editor) connects to:
    ws://host/ws/website/<website_pk>/

On connection the client is added to the channel group:
    website_lock_{website_pk}

The server broadcasts two event types over this group:
    • lock_acquired  — another user has started editing; clients should disable edit mode
    • lock_released  — the editor left; clients may now request the lock

Clients never send messages to the server through this socket;
all state mutations go through the HTTP endpoints.
"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer


def lock_group_name(website_pk: int | str) -> str:
    return f"website_lock_{website_pk}"


class WebsiteLockConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.website_pk = self.scope["url_route"]["kwargs"]["website_pk"]
        self.group_name = lock_group_name(self.website_pk)

        # user = self.scope.get("user") TODO: After authentication is set up, uncomment this to enforce auth on the WebSocket connection
        # if user is None or not user.is_authenticated:
        #     await self.close(code=4001)
        #     return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # ── Incoming messages from channel layer (sent by HTTP views via broadcast helpers) ──

    async def lock_acquired(self, event):
        """Relay 'lock acquired' to this client."""
        await self.send_json(
            {
                "type": "lock_acquired",
                "user_id": event["user_id"],
                "website_pk": self.website_pk,
            }
        )

    async def lock_released(self, event):
        """Relay 'lock released' to this client."""
        await self.send_json(
            {
                "type": "lock_released",
                "website_pk": self.website_pk,
            }
        )
