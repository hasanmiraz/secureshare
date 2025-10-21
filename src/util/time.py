from datetime import datetime, timezone

def now_ts() -> float:
    return datetime.now(tz=timezone.utc).timestamp()

def pretty_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
