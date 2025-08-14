import csv
import os
from contextvars import ContextVar
from datetime import datetime, timezone
from io import StringIO
import tzlocal
import time

from alibabacloud_bssopenapi20171214.client import Client as BssOpenApi20171214Client
from alibabacloud_rds20140815.client import Client as RdsClient
from alibabacloud_tea_openapi.models import Config
from alibabacloud_vpc20160428.client import Client as VpcClient
from alibabacloud_das20200116.client import Client as DAS20200116Client

current_request_headers: ContextVar[dict] = ContextVar("current_request_headers", default={})

PERF_KEYS = {
    "mysql": {
        "MemCpuUsage": ["MySQL_MemCpuUsage"],
        "QPSTPS": ["MySQL_QPSTPS"],
        "Sessions": ["MySQL_Sessions"],
        "COMDML": ["MySQL_COMDML"],
        "RowDML": ["MySQL_RowDML"],
        "SpaceUsage": ["MySQL_DetailedSpaceUsage"],
        "ThreadStatus": ["MySQL_ThreadStatus"],
        "MBPS": ["MySQL_MBPS"],
        "DetailedSpaceUsage": ["MySQL_DetailedSpaceUsage"]
    },
    "pgsql": {
        "MemCpuUsage": ["MemoryUsage", "CpuUsage"],
        "QPSTPS": ["PolarDBQPSTPS"],
        "Sessions": ["PgSQL_Session"],
        "COMDML": ["PgSQL_COMDML"],
        "RowDML": ["PolarDBRowDML"],
        "SpaceUsage": ["PgSQL_SpaceUsage"],
        "ThreadStatus": [],
        "MBPS": [],
        "DetailedSpaceUsage": ["SQLServer_DetailedSpaceUsage"]
    },
    "sqlserver": {
        "MemCpuUsage": ["SQLServer_CPUUsage"],
        "QPSTPS": ["SQLServer_QPS", "SQLServer_IOPS"],
        "Sessions": ["SQLServer_Sessions"],
        "COMDML": [],
        "RowDML": [],
        "SpaceUsage": ["SQLServer_DetailedSpaceUsage"],
        "ThreadStatus": [],
        "MBPS": [],
        "DetailedSpaceUsage": ["PgSQL_SpaceUsage"]
    }

}

DAS_KEYS = {
    "mysql": {
        "DiskUsage": ["disk_usage"],
        "IOPSUsage": ["data_iops_usage"],
        "IOBytesPS": ["data_io_bytes_ps"],
        "MdlLockSession": ["mdl_lock_session"]
    }
}

INSTANCE_MAX_IO_MAP = {
    # 独享型
    "x2.medium": 125,
    "x4.medium": 125,
    "x8.medium": 125,
    "x2.large": 187.5,
    "x4.large": 187.5,
    "x8.large": 187.5,
    "x2.xlarge": 250,
    "x4.xlarge": 250,
    "x8.xlarge": 250,
    "x2.3large": 312.5,
    "x4.3large": 312.5,
    "x8.3large": 312.5,
    "x2.2xlarge": 375,
    "x4.2xlarge": 375,
    "x8.2xlarge": 375,
    "x2.3xlarge": 500,
    "x4.3xlarge": 500,
    "x8.3xlarge": 500,
    "x2.4xlarge": 625,
    "x4.4xlarge": 625,
    "x8.4xlarge": 625,
    "x2.13large": 1000,
    "x4.13large": 1000,
    "x8.13large": 1000,
    "x2.8xlarge": 1025,
    "x4.8xlarge": 1025,
    "x8.8xlarge": 1025,
    "x2.13xlarge": 2000,
    "x4.13xlarge": 2000,
    "x8.13xlarge": 2000,
    "x4.16xlarge": 2560,
    
    # 倚天版（ARM架构）规格
    "x4m.medium": 125,
    "x8m.medium": 125,
    "x2m.large": 187.5,
    "x4m.large": 187.5,
    "x8m.large": 187.5,
    "x2m.xlarge": 250,
    "x4m.xlarge": 250,
    "x8m.xlarge": 250,
    "x2m.2xlarge": 375,
    "x4m.2xlarge": 375,
    "x8m.2xlarge": 375,
    "x2m.4xlarge": 512.5,
    "x4m.4xlarge": 512.5,
    "x4m.8xlarge": 1025,
    "x8m.8xlarge": 1000,

    # 倚天集群版（ARM架构）规格
    "x4e.medium": 125,
    "x8e.medium": 125,
    "x2e.large": 187.5,
    "x4e.large": 187.5,
    "x8e.large": 187.5,
    "x2e.xlarge": 250,
    "x4e.xlarge": 250,
    "x8e.xlarge": 250,
    "x2e.2xlarge": 375,
    "x4e.2xlarge": 375,
    "x8e.2xlarge": 375,
    "x2e.4xlarge": 512.5,
    "x4e.4xlarge": 512.5,
    "x8e.4xlarge": 512.5,
    "x2e.8xlarge": 1000,
    "x4e.8xlarge": 1025,
    "x8e.8xlarge": 1000
}


def parse_args(argv):
    args = {}
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg.startswith('--'):
            key = arg[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith('--'):
                args[key] = argv[i+1]
                i += 2
            else:
                args[key] = True
                i += 1
    return args


def transform_to_iso_8601(dt: datetime, timespec: str):
    return dt.astimezone(timezone.utc).isoformat(timespec=timespec).replace("+00:00", "Z")

def parse_iso_8601(s: str) -> datetime:
    """
    将 ISO 8601 格式字符串（支持 Z 时区标记）转换为 datetime 对象。
    """
    # 替换 'Z' 为 '+00:00'，以便正确解析为 UTC 时间
    s = s.replace("Z", "+00:00")
    # 解析字符串为 UTC 时间的 datetime 对象
    dt_utc = datetime.fromisoformat(s)
    # 获取本地时区
    local_tz = tzlocal.get_localzone()
    # 转换为本地时区时间
    dt_local = dt_utc.astimezone(local_tz)
    return dt_local.replace(tzinfo=None)

def transform_timestamp_to_datetime(timestamp: int):
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

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

def transform_das_key(db_type: str, das_keys: list[str]):
    das_key_after_transform = []
    for key in das_keys:
        if key in DAS_KEYS[db_type.lower()]:
            das_key_after_transform.extend(DAS_KEYS[db_type.lower()][key])
        else:
            das_key_after_transform.append(key)
    return das_key_after_transform


def json_array_to_csv(data):
    if not data or not isinstance(data, list):
        return ""

    fieldnames = set()
    for item in data:
        if isinstance(item, dict):
            fieldnames.update(item.keys())
        elif hasattr(item, 'to_map'):
            fieldnames.update(item.to_map().keys())

    if not fieldnames:
        return ""

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=sorted(fieldnames))

    writer.writeheader()
    for item in data:
        if isinstance(item, dict):
            writer.writerow({k: v if v is not None else '' for k, v in item.items()})
        elif hasattr(item, 'to_map'):
            writer.writerow({k: v if v is not None else '' for k, v in item.to_map().items()})

    return output.getvalue()


def json_array_to_markdown(headers, datas):
    if not headers or not isinstance(headers, list):
        return ""
    if not datas or not isinstance(datas, list):
        return ""
    
    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in datas:
        if isinstance(row, dict):
            markdown_table += "| " + " | ".join(str(row.get(header, '-')) for header in headers) + " |\n"
        else:
            markdown_table += "| " + " | ".join(map(str, row)) + " |\n"
    return markdown_table

def get_instance_max_iombps(instance_attribute):
    """
        计算规则参考 https://help.aliyun.com/zh/rds/product-overview/primary-apsaradb-rds-instance-types?spm=a2c4g.11186623.help-menu-26090.d_0_0_6_1.1ca8798519jnKx#af0e23b6e5t6w
    """
    instance_class = instance_attribute['DBInstanceClass']
    # 提取核心规格代码
    # 例如: mysql.x2.medium.2c -> x2.medium
    # 例如: mysqlro.x4.large.1c -> x4.large
    parts = instance_class.split('.')
    
    # 如果至少有3部分，取中间的部分作为核心规格代码
    if len(parts) >= 3:
        stripped_instance_class = '.'.join(parts[1:3])
    else:
        stripped_instance_class = instance_class

    storage_type = instance_attribute['DBInstanceStorageType']
    instance_storage = instance_attribute['DBInstanceStorage']
    max_iombps = None
    instance_max_io = INSTANCE_MAX_IO_MAP.get(stripped_instance_class, None)
    storage_max_io = 120 + 0.5 * instance_storage
    if storage_type.startswith('cloud'):
        if instance_max_io is not None:
            max_iombps = min(instance_max_io, storage_max_io)
        else:
            max_iombps = storage_max_io
        if storage_type == 'cloud_essd':
            max_iombps = min(350, max_iombps)
        elif storage_type == 'cloud_essd2':
            max_iombps = min(750, max_iombps)
        elif storage_type == 'cloud_essd3':
            max_iombps = min(4000, max_iombps)
        else:
            max_iombps = min(300, max_iombps)
    elif storage_type == 'general_essd':
        if instance_attribute["BurstingEnabled"]:
            if instance_max_io is not None:
                max_iombps = min(4000, instance_max_io)
            else:
                max_iombps = 4000
        else:
            if instance_max_io is not None:
                max_iombps = min(storage_max_io, instance_max_io)
            else:
                max_iombps = storage_max_io
            max_iombps = min(350, max_iombps)
    return max_iombps

def convert_datetime_to_timestamp(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    timestamp_seconds = time.mktime(dt.timetuple())
    timestamp_milliseconds = int(timestamp_seconds) * 1000
    return timestamp_milliseconds


def get_rds_account():
    header = current_request_headers.get()
    user = header.get("rds_user") if header else None
    passwd = header.get("rds_passwd") if header else None
    if user and passwd:
        return user, passwd
    return None, None


def get_aksk():
    ak = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    sk = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    sts = os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN')
    header = current_request_headers.get()
    if header and (header.get("ak") or header.get("sk") or header.get("sts")):
        ak, sk, sts = header.get("ak"), header.get("sk"), header.get("sts")
    return ak, sk, sts


def get_rds_client(region_id: str):
    ak, sk, sts = get_aksk()
    config = Config(
        access_key_id=ak,
        access_key_secret=sk,
        security_token=sts,
        region_id=region_id,
        protocol="https",
        connect_timeout=10 * 1000,
        read_timeout=300 * 1000
    )
    client = RdsClient(config)
    return client


def get_vpc_client(region_id: str) -> VpcClient:
    """Get VPC client instance.

    Args:
        region_id: The region ID for the VPC client.

    Returns:
        VpcClient: The VPC client instance for the specified region.
    """
    ak, sk, sts = get_aksk()
    config = Config(
        access_key_id=ak,
        access_key_secret=sk,
        security_token=sts,
        region_id=region_id,
        protocol="https",
        connect_timeout=10 * 1000,
        read_timeout=300 * 1000
    )
    return VpcClient(config)


def get_bill_client(region_id: str):
    ak, sk, sts = get_aksk()
    config = Config(
        access_key_id=ak,
        access_key_secret=sk,
        security_token=sts,
        region_id=region_id,
        protocol="https",
        connect_timeout=10 * 1000,
        read_timeout=300 * 1000
    )
    client = BssOpenApi20171214Client(config)
    return client


def get_das_client():
    ak, sk, sts = get_aksk()
    config = Config(
        access_key_id=ak,
        access_key_secret=sk,
        security_token=sts,
        region_id='cn-shanghai',
        protocol="https",
        connect_timeout=10 * 1000,
        read_timeout=300 * 1000
    )
    client = DAS20200116Client(config)
    return client
