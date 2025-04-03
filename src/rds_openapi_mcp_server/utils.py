from datetime import datetime


def transform_to_iso_8601(dt: datetime, timespec: str):
    return dt.isoformat(timespec=timespec) + "Z"


def transform_to_datetime(s: str):
    try:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%Sz")
    except ValueError:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%Mz")
    return dt
