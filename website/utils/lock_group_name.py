def lock_group_name(website_pk: int | str) -> str:
    """Return the channel group name for a given website_pk."""

    return f"website_lock_{website_pk}"
