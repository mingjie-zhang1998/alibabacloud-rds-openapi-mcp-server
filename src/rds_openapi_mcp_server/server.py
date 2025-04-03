from datetime import datetime
from http.client import HTTPException
from mcp.server.fastmcp import FastMCP
import os
from alibabacloud_rds20140815 import models as rds_20140815_models
from alibabacloud_rds20140815.client import Client as RdsClient
from alibabacloud_tea_openapi.models import Config
from pydantic import BaseModel, Field
from utils import transform_to_iso_8601, transform_to_datetime

mcp = FastMCP("Alibaba Cloud RDS OPENAPI")


def get_rds_client(region_id: str):
    config = Config(
        access_key_id=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),  # 或直接赋值
        access_key_secret=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        region_id=region_id,
        protocol="https"
    )
    client = RdsClient(config)
    return client


@mcp.tool()
async def describe_db_instances(region_id: str):
    """
    Queries instances.
    Args:
        region_id: queries instances in region id(e.g. cn-hangzhou)
    :return:
    """
    client = get_rds_client(region_id)
    try:
        request = rds_20140815_models.DescribeDBInstancesRequest(region_id=region_id)
        response = client.describe_dbinstances(request)
        return response.body.to_map()
    except Exception as e:
        raise e


@mcp.tool()
async def describe_db_instance_attribute(region_id: str, db_instance_id: str):
    """
    Queries the details of an instance.
    Args:
        region_id: db instance region(e.g. cn-hangzhou)
        db_instance_id: db instance id(e.g. rm-xxx)
    :return:
    """
    client = get_rds_client(region_id)
    try:
        request = rds_20140815_models.DescribeDBInstanceAttributeRequest(dbinstance_id=db_instance_id)
        response = client.describe_dbinstance_attribute(request)
        return response.body.to_map()
    except Exception as e:
        raise e


def _get_db_instance_performance_data(region_id: str, db_instance_id: str, start_time: datetime, end_time: datetime):
    client = get_rds_client(region_id)
    mysql_perf_keys = [
        "MySQL_QPSTPS",
        "MySQL_NetworkTraffic",
        "MySQL_Sessions",
        "MySQL_COMDML",
        "MySQL_ROWDML",
        "MySQL_MemCpuUsage",
        "MySQL_IOPS",
        "MySQL_ThreadStatus"
    ]
    perf_datas = {}
    for key in mysql_perf_keys:
        try:
            request = rds_20140815_models.DescribeDBInstancePerformanceRequest(
                dbinstance_id=db_instance_id,
                start_time=transform_to_iso_8601(start_time, "minutes"),
                end_time=transform_to_iso_8601(end_time, "minutes"),
                key=key
            )
            response = client.describe_dbinstance_performance(request)
            perf_datas[key] = response.body.to_map()
        except Exception as e:
            raise e
    perf_info = "\n".join([f"{k}: {v}" for k, v in perf_datas.items()])
    return perf_info


def _get_db_instance_error_logs(region_id: str, db_instance_id: str, start_time: datetime, end_time: datetime):
    client = get_rds_client(region_id)
    try:
        request = rds_20140815_models.DescribeErrorLogsRequest(
            dbinstance_id=db_instance_id,
            start_time=transform_to_iso_8601(start_time, "minutes"),
            end_time=transform_to_iso_8601(end_time, "minutes"),
            page_size=100,
        )
        response = client.describe_error_logs(request)
        error_logs = "\n".join(response.body.to_map()['Items']['ErrorLog'])
        return error_logs
    except Exception as e:
        raise e


def _get_db_instance_sql_reports(region_id: str, db_instance_id: str, start_time: datetime, end_time: datetime):
    client = get_rds_client(region_id)
    try:
        request = rds_20140815_models.DescribeSQLLogReportListRequest(
            dbinstance_id=db_instance_id,
            start_time=transform_to_iso_8601(start_time, "seconds"),
            end_time=transform_to_iso_8601(end_time, "seconds"),
        )
        response = client.describe_sqllog_report_list(request)
        return response.body.to_map()['Items']
    except Exception as e:
        raise e


@mcp.tool()
async def describe_db_instance_metrics(region_id: str, db_instance_id: str, start_time: str, end_time: str):
    """
    Queries the performance data、error log and sql reports of an instance.
    Args:
        region_id: db instance region(e.g. cn-hangzhou)
        db_instance_id: db instance id(e.g. rm-xxx)
        start_time: start time UTC TimeZone (e.g. 2023-01-01T00:00Z)
        end_time: end time UTC TimeZone (e.g. 2023-01-01T00:00Z)
    """
    try:
        start_time = transform_to_datetime(start_time)
        end_time = transform_to_datetime(end_time)
        perf_data = _get_db_instance_performance_data(region_id, db_instance_id, start_time, end_time)
        error_log = _get_db_instance_error_logs(region_id, db_instance_id, start_time, end_time)
        sql_report = _get_db_instance_sql_reports(region_id, db_instance_id, start_time, end_time)
        print(perf_data)
        print(error_log)
        print(sql_report)
        return f"""
## Performance Data
{perf_data}
## Error Log
{error_log}
## SQL Report
{sql_report}
"""
    except Exception as e:
        raise e


if __name__ == '__main__':
    # Initialize and run the server
    mcp.run(transport='sse')
