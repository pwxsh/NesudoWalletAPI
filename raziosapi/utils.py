from datetime import datetime


def utc_timestamp() -> float:
    return datetime.utcnow().timestamp()
