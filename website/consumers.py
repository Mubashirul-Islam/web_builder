from channels.generic.websocket import AsyncJsonWebsocketConsumer

from website.utils.lock_group_name import lock_group_name


class WebsiteLockConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer to relay website lock events to clients in real-time."""

    async def connect(self):
        """On WebSocket connection, add this channel to the lock group for the relevant website."""
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
