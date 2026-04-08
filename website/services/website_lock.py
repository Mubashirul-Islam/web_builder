from django.core.cache import cache


class WebsiteLock:
    """Website lock mechanism for website editing, using Django's cache framework (e.g. Redis)."""
    
    lock_ttl_seconds = 300 # 5 minutes

    @classmethod
    def locked_by(cls, website_pk: int) -> int | None:
        """
        Return the user ID that owns the lock, or None if no lock exists.
        """
        return cache.get(website_pk)

    @classmethod
    def acquire_lock(cls, website_pk: int, user_id: int) -> bool:
        """
        Attempt to atomically acquire the lock for `website_pk`.
        Uses add() which only sets the key if it does NOT already exist.
        Returns True if the lock was acquired, False if already held by someone else.
        If already held by the SAME user, refreshes TTL and returns True.
        """
        key = website_pk
        value = user_id

        # add() is atomic: sets only if key absent (NX behaviour)
        acquired = cache.add(key, value, timeout=cls.lock_ttl_seconds)
        if acquired:
            return True

        # Key already exists — check if it belongs to this user
        existing_user = cls.locked_by(key)
        if existing_user == user_id:
            # Same user re-entering (e.g. page refresh) — refresh TTL
            cache.set(key, value, timeout=cls.lock_ttl_seconds)
            return True

        return False

    @classmethod
    def refresh_lock(cls, website_pk: int, user_id: int) -> bool:
        """
        Extend the TTL of an existing lock.
        Returns True if the lock exists and belongs to this user, False otherwise.
        """
        key = website_pk
        existing_user = cls.locked_by(key)

        if not existing_user:
            return False

        if existing_user != user_id:
            return False

        cache.set(key, existing_user, timeout=cls.lock_ttl_seconds)
        return True

    @classmethod
    def release_lock(cls, website_pk: int, user_id: int) -> bool:
        """
        Release the lock only if it belongs to the requesting user.
        Returns True if released, False if not held by this user (or already gone).
        """
        key = website_pk
        existing_user = cls.locked_by(key)

        if not existing_user:
            # Already expired — treat as success (idempotent)
            return True

        if existing_user != user_id:
            return False

        cache.delete(key)
        return True

    @classmethod
    def check_lock_for_save(cls, website_pk: int, user_id: int) -> tuple[bool, bool]:
        """
        Before saving, verify:
          1. The lock still exists (not expired).
          2. It belongs to this user.

        Returns (lock_exists: bool, is_same_user: bool)
        """
        key = website_pk
        existing_user = cls.locked_by(key)
        if not existing_user:
            return False, False
        return True, existing_user == user_id
