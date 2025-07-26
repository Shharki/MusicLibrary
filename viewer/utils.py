def format_seconds(seconds: int) -> str:
    if seconds is None:
        return None
    mins, secs = divmod(seconds, 60)
    return f"{mins}:{secs:02}"