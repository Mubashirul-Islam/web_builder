"""
Utility functions to push lock events from HTTP views into the WebSocket channel layer.
Call these after mutating Redis state so all connected clients are notified.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from website.consumers import lock_group_name


def broadcast_lock_acquired(website_pk: int, user_id: int) -> None:
    """
    Notify all subscribers that `user_id` has acquired the edit lock.
    Other clients should disable their edit controls.
    """
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        lock_group_name(website_pk),
        {
            "type": "lock_acquired",  # maps to WebsiteLockConsumer.lock_acquired()
            "user_id": user_id,
        },
    )


def broadcast_lock_released(website_pk: int) -> None:
    """
    Notify all subscribers that the edit lock is now free.
    Clients may transition from view mode to edit mode.
    """
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        lock_group_name(website_pk),
        {
            "type": "lock_released",  # maps to WebsiteLockConsumer.lock_released()
        },
    )
