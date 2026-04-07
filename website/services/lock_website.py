from django.conf import settings
from django.core.cache import cache


LOCK_TTL_SECONDS = getattr(settings, "WEBSITE_LOCK_TTL_SECONDS", 300)  # 5 minutes
HEARTBEAT_INTERVAL_SECONDS = getattr(
    settings, "WEBSITE_HEARTBEAT_INTERVAL_SECONDS", 120
)  # 2 minutes


def locked_by(website_pk: int) -> dict | None:
    """
    Return the lock data dict {"user_id": ..., "ttl": ...} if the lock exists,
    or None if there is no active lock.
    """
    return cache.get(website_pk)


def acquire_lock(website_pk: int, user_id: int) -> bool:
    """
    Attempt to atomically acquire the lock for `website_pk`.
    Uses add() which only sets the key if it does NOT already exist.
    Returns True if the lock was acquired, False if already held by someone else.
    If already held by the SAME user, refreshes TTL and returns True.
    """
    key = website_pk
    value = user_id

    # add() is atomic: sets only if key absent (NX behaviour)
    acquired = cache.add(key, value, timeout=LOCK_TTL_SECONDS)
    if acquired:
        return True

    # Key already exists — check if it belongs to this user
    existing_user = locked_by(key)
    if existing_user == user_id:
        # Same user re-entering (e.g. page refresh) — refresh TTL
        cache.set(key, value, timeout=LOCK_TTL_SECONDS)
        return True

    return False


def refresh_lock(website_pk: int, user_id: int) -> bool:
    """
    Extend the TTL of an existing lock (heartbeat).
    Returns True if the lock exists and belongs to this user, False otherwise.
    """
    key = website_pk
    existing_user = locked_by(key)

    if not existing_user:
        return False

    if existing_user != user_id:
        return False

    cache.set(key, existing_user, timeout=LOCK_TTL_SECONDS)
    return True


def release_lock(website_pk: int, user_id: int) -> bool:
    """
    Release the lock only if it belongs to the requesting user.
    Returns True if released, False if not held by this user (or already gone).
    """
    key = website_pk
    existing_user = locked_by(key)

    if not existing_user:
        # Already expired — treat as success (idempotent)
        return True

    if existing_user != user_id:
        return False

    cache.delete(key)
    return True


def check_lock_for_save(website_pk: int, user_id: int) -> tuple[bool, bool]:
    """
    Before saving, verify:
      1. The lock still exists (not expired).
      2. It belongs to this user.

    Returns (lock_exists: bool, is_same_user: bool)
    """
    key = website_pk
    existing_user = locked_by(key)
    if not existing_user:
        return False, False
    return True, existing_user == user_id
