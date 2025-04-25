from datetime import datetime, timezone


PERF_KEYS = {
    "mysql": {
        "MemCpuUsage": ["MySQL_MemCpuUsage"],
        "QPSTPS": ["MySQL_QPSTPS"],
        "Sessions": ["MySQL_Sessions"],
        "COMDML": ["MySQL_COMDML"],
        "RowDML": ["MySQL_RowDML"],
        "SpaceUsage": ["MySQL_DetailedSpaceUsage"]
    },
    "pgsql": {
        "MemCpuUsage": ["MemoryUsage", "CpuUsage"],
        "QPSTPS": ["PolarDBQPSTPS"],
        "Sessions": ["PgSQL_Session"],
        "COMDML": ["PgSQL_COMDML"],
        "RowDML": ["PolarDBRowDML"],
        "SpaceUsage": ["PgSQL_SpaceUsage"]
    },
    "sqlserver": {
        "MemCpuUsage": ["SQLServer_CPUUsage"],
        "QPSTPS": ["SQLServer_QPS", "SQLServer_IOPS"],
        "Sessions": ["SQLServer_Sessions"],
        "COMDML": [],
        "RowDML": [],
        "SpaceUsage": ["SQLServer_DetailedSpaceUsage"],
    }

}

def transform_to_iso_8601(dt: datetime, timespec: str):
    return dt.astimezone(timezone.utc).isoformat(timespec=timespec).replace("+00:00", "Z")


def transform_to_datetime(s: str):
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
    return dt


def transform_perf_key(db_type: str, perf_keys: list[str]):
    perf_key_after_transform = []
    for key in perf_keys:
        if key in PERF_KEYS[db_type.lower()]:
            perf_key_after_transform.extend(PERF_KEYS[db_type.lower()][key])
        else:
            perf_key_after_transform.append(key)
    return perf_key_after_transform


def compress_json_array(json_array: list[dict]):
    if not json_array or len(json_array) == 0:
        return ""
    compress_str = ";".join(json_array[0].keys())
    for item in json_array:
        compress_str += "|" + ";".join([str(item[key]) for key in json_array[0].keys()])
    return compress_str
