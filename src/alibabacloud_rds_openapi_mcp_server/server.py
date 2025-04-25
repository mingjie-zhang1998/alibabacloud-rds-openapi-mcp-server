import json
import logging
import os
import sys

from typing import Dict, Any, List
from alibabacloud_rds20140815 import models as rds_20140815_models
from alibabacloud_rds20140815.client import Client as RdsClient
from alibabacloud_tea_openapi.models import Config
from alibabacloud_vpc20160428 import models as vpc_20160428_models
from alibabacloud_vpc20160428.client import Client as VpcClient
from mcp.server.fastmcp import FastMCP
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from utils import transform_to_iso_8601, transform_to_datetime, transform_perf_key

logger = logging.getLogger(__name__)

mcp = FastMCP("Alibaba Cloud RDS OPENAPI")


def get_rds_client(region_id: str):
    config = Config(
        access_key_id=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        access_key_secret=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
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
        region_id (str): The region ID for the VPC client.

    Returns:
        VpcClient: The VPC client instance for the specified region.
    """
    config = Config(
        access_key_id=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        access_key_secret=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        region_id=region_id,
        protocol="https",
        connect_timeout=10 * 1000,
        read_timeout=300 * 1000
    )
    return VpcClient(config)


class OpenAPIError(Exception):
    """Custom exception for RDS OpenAPI related errors."""
    pass


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


@mcp.tool()
async def describe_db_instance_performance(region_id: str, db_instance_id: str, db_type: str, perf_key: str,
                                           start_time: str, end_time: str):
    """
    Queries the performance data of an instance.
    Args:
        region_id: db instance region(e.g. cn-hangzhou)
        db_instance_id: db instance id(e.g. rm-xxx)
        db_type: the db instance database type(e.g. mysql,pgsql,sqlserver)
        perf_key: Performance Key(e.g. MemCpuUsage,QPSTPS,Sessions,COMDML,RowDML)
        start_time: start time(e.g. 2023-01-01 00:00)
        end_time: end time(e.g. 2023-01-01 00:00)
    """
    try:
        start_time = transform_to_datetime(start_time)
        end_time = transform_to_datetime(end_time)
        client = get_rds_client(region_id)
        perf_key = transform_perf_key(db_type, perf_key)
        if not perf_key:
            raise OpenAPIError(f"Unsupported perf_key: {perf_key}")
        request = rds_20140815_models.DescribeDBInstancePerformanceRequest(
            dbinstance_id=db_instance_id,
            start_time=transform_to_iso_8601(start_time, "minutes"),
            end_time=transform_to_iso_8601(end_time, "minutes"),
            key=",".join(perf_key)
        )
        response = client.describe_dbinstance_performance(request)
        responses = []
        for perf_key in response.body.performance_keys.performance_key:
            perf_key_info = f"""Key={perf_key.key}; Unit={perf_key.unit}; ValueFormat={perf_key.value_format}; Values={"|".join([f"{value.date} {value.value}" for value in perf_key.values.performance_value])}"""
            responses.append(perf_key_info)
        return responses
    except Exception as e:
        raise e


@mcp.tool()
async def modify_parameter(
        region_id: str,
        dbinstance_id: str,
        parameters: Dict[str, str] = None,
        parameter_group_id: str = None,
        forcerestart: bool = False,
        switch_time_mode: str = "Immediate",
        switch_time: str = None,
        client_token: str = None
) -> Dict[str, Any]:
    """Modify RDS instance parameters.

    Args:
        region_id (str): The region ID of the RDS instance.
        dbinstance_id (str): The ID of the RDS instance.
        parameters (Dict[str, str], optional): Parameters and their values in JSON format.
            Example: {"delayed_insert_timeout": "600", "max_length_for_sort_data": "2048"}
        parameter_group_id (str, optional): Parameter template ID.
        forcerestart (bool, optional): Whether to force restart the database. Default: False.
        switch_time_mode (str, optional): Execution time mode. Values: Immediate, MaintainTime, ScheduleTime. Default: Immediate.
        switch_time (str, optional): Scheduled execution time in format: yyyy-MM-ddTHH:mm:ssZ (UTC time).
        client_token (str, optional): Client token for idempotency, max 64 ASCII characters.

    Returns:
        Dict[str, Any]: The response containing the request ID.
    """
    try:
        # Initialize the client
        client = get_rds_client(region_id)

        # Create request
        request = rds_20140815_models.ModifyParameterRequest(
            dbinstance_id=dbinstance_id,
            forcerestart=forcerestart,
            switch_time_mode=switch_time_mode
        )

        # Add optional parameters if provided
        if parameters:
            request.parameters = json.dumps(parameters)
        if parameter_group_id:
            request.parameter_group_id = parameter_group_id
        if switch_time:
            request.switch_time = switch_time
        if client_token:
            request.client_token = client_token

        # Make the API request
        response = client.modify_parameter(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while modifying parameters: {str(e)}")
        raise OpenAPIError(f"Failed to modify RDS instance parameters: {str(e)}")


@mcp.tool()
async def modify_db_instance_spec(
        region_id: str,
        dbinstance_id: str,
        dbinstance_class: str = None,
        dbinstance_storage: int = None,
        pay_type: str = None,
        effective_time: str = None,
        switch_time: str = None,
        switch_time_mode: str = None,
        source_biz: str = None,
        dedicated_host_group_id: str = None,
        zone_id: str = None,
        vswitch_id: str = None,
        category: str = None,
        instance_network_type: str = None,
        direction: str = None,
        auto_pause: bool = None,
        max_capacity: float = None,
        min_capacity: float = None,
        switch_force: bool = None,
        client_token: str = None
) -> Dict[str, Any]:
    """Modify RDS instance specifications.

    Args:
        region_id (str): The region ID of the RDS instance.
        dbinstance_id (str): The ID of the RDS instance.
        dbinstance_class (str, optional): Target instance specification.
        dbinstance_storage (int, optional): Target storage space in GB.
        pay_type (str, optional): Instance payment type. Values: Postpaid, Prepaid, Serverless.
        effective_time (str, optional): When the new configuration takes effect. Values: Immediate, MaintainTime, ScheduleTime.
        switch_time (str, optional): Scheduled switch time in format: yyyy-MM-ddTHH:mm:ssZ (UTC time).
        switch_time_mode (str, optional): Switch time mode. Values: Immediate, MaintainTime, ScheduleTime.
        source_biz (str, optional): Source business type.
        dedicated_host_group_id (str, optional): Dedicated host group ID.
        zone_id (str, optional): Zone ID.
        vswitch_id (str, optional): VSwitch ID.
        category (str, optional): Instance category.
        instance_network_type (str, optional): Instance network type.
        direction (str, optional): Specification change direction. Values: UP, DOWN.
        auto_pause (bool, optional): Whether to enable auto pause for Serverless instances.
        max_capacity (float, optional): Maximum capacity for Serverless instances.
        min_capacity (float, optional): Minimum capacity for Serverless instances.
        switch_force (bool, optional): Whether to force switch for Serverless instances.
        client_token (str, optional): Client token for idempotency, max 64 ASCII characters.

    Returns:
        Dict[str, Any]: The response containing the request ID.
    """
    try:
        # Initialize the client
        client = get_rds_client(region_id)

        # Create request
        request = rds_20140815_models.ModifyDBInstanceSpecRequest(
            dbinstance_id=dbinstance_id
        )

        # Add optional parameters if provided
        if dbinstance_class:
            request.dbinstance_class = dbinstance_class
        if dbinstance_storage:
            request.dbinstance_storage = dbinstance_storage
        if pay_type:
            request.pay_type = pay_type
        if effective_time:
            request.effective_time = effective_time
        if switch_time:
            request.switch_time = switch_time
        if switch_time_mode:
            request.switch_time_mode = switch_time_mode
        if source_biz:
            request.source_biz = source_biz
        if dedicated_host_group_id:
            request.dedicated_host_group_id = dedicated_host_group_id
        if zone_id:
            request.zone_id = zone_id
        if vswitch_id:
            request.vswitch_id = vswitch_id
        if category:
            request.category = category
        if instance_network_type:
            request.instance_network_type = instance_network_type
        if direction:
            request.direction = direction
        if auto_pause is not None:
            request.auto_pause = auto_pause
        if max_capacity:
            request.max_capacity = max_capacity
        if min_capacity:
            request.min_capacity = min_capacity
        if switch_force is not None:
            request.switch_force = switch_force
        if client_token:
            request.client_token = client_token

        # Make the API request
        response = client.modify_dbinstance_spec(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while modifying instance specifications: {str(e)}")
        raise OpenAPIError(f"Failed to modify RDS instance specifications: {str(e)}")


@mcp.tool()
async def describe_available_classes(
        region_id: str,
        zone_id: str,
        instance_charge_type: str,
        engine: str,
        engine_version: str,
        dbinstance_storage_type: str,
        category: str,
        dbinstance_id: str = None,
        order_type: str = None,
        commodity_code: str = None
) -> Dict[str, Any]:
    """Query the RDS instance class_code and storage space that can be purchased in the inventory.

    Args:
        region_id (str): The region ID of the RDS instance.
        zone_id (str): The zone ID of the RDS instance. Query available zones by `describe_available_zones`.
        instance_charge_type (str): Instance payment type. Values: Prepaid, Postpaid, Serverless.
        engine (str): Database engine type. Values: MySQL, SQLServer, PostgreSQL, MariaDB.
        engine_version (str): Database version.
        dbinstance_storage_type (str): Storage type. Values: local_ssd,general_essd,cloud_essd,cloud_essd2,cloud_essd3
        category (str): Instance category. Values: Basic, HighAvailability, cluster, AlwaysOn, Finance, serverless_basic, serverless_standard, serverless_ha.
        dbinstance_id (str, optional): The ID of the RDS instance.
        order_type (str, optional): Order type. Currently only supports "BUY".
        commodity_code (str, optional): Commodity code for read-only instances.

    Returns:
        Dict[str, Any]: The response containing available instance classes and storage ranges.
    """
    try:
        # Initialize the client
        client = get_rds_client(region_id)

        # Create request
        request = rds_20140815_models.DescribeAvailableClassesRequest(
            region_id=region_id,
            zone_id=zone_id,
            instance_charge_type=instance_charge_type,
            engine=engine,
            engine_version=engine_version,
            dbinstance_storage_type=dbinstance_storage_type,
            category=category
        )

        # Add optional parameters if provided
        if dbinstance_id:
            request.dbinstance_id = dbinstance_id
        if order_type:
            request.order_type = order_type
        if commodity_code:
            request.commodity_code = commodity_code

        # Make the API request
        response = client.describe_available_classes(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while querying available classes: {str(e)}")
        raise OpenAPIError(f"Failed to query available instance classes: {str(e)}")


@mcp.tool()
async def create_db_instance(
        region_id: str,
        engine: str,
        engine_version: str,
        dbinstance_class: str,
        dbinstance_storage: int,
        vpc_id: str,
        vswitch_id: str,
        zone_id: str,
        security_ip_list: str = "127.0.0.1",
        instance_network_type: str = "VPC",
        pay_type: str = "Postpaid",
        instance_charge_type: str = None,
        system_db_charset: str = None,
        dbinstance_net_type: str = "Internet",
        category: str = "Basic",
        dbinstance_storage_type: str = None,
        private_ip_address: str = None,
        client_token: str = None,
        resource_group_id: str = None,
        dedicated_host_group_id: str = None,
        tde_status: str = None,
        encryption_key: str = None,
        serverless_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create an RDS instance.

    Args:
        region_id (str): Region ID.
        engine (str): Database type (MySQL, SQLServer, PostgreSQL, MariaDB).
        engine_version (str): Database version.
        dbinstance_class (str): Instance specification. Query available class_codes by `describe_available_classes`.
        dbinstance_storage (int): Storage space in GB.
        security_ip_list (str): IP whitelist, separated by commas. Default: "127.0.0.1".
        instance_network_type (str, optional): Network type (Classic, VPC). Default: VPC.
        zone_id (str, optional): Zone ID. Query available zones by `describe_available_zones`.
        pay_type (str, optional): Payment type (Postpaid, Prepaid). Default: Postpaid.
        instance_charge_type (str, optional): Instance charge type.
        system_db_charset (str, optional): Character set.
        dbinstance_net_type (str, optional): Network connection type (Internet, Intranet). Default: Internet.
        category (str, optional): Instance category. Default: Basic.
        dbinstance_storage_type (str, optional): Storage type. (e.g. local_ssd,general_essd,cloud_essd,cloud_essd2,cloud_essd3)
        vpc_id (str): VPC ID.
        vswitch_id (str): VSwitch ID.
        private_ip_address (str, optional): Private IP address.
        client_token (str, optional): Idempotence token.
        resource_group_id (str, optional): Resource group ID.
        dedicated_host_group_id (str, optional): Dedicated host group ID.
        tde_status (str, optional): TDE status (Enable, Disable).
        encryption_key (str, optional): Custom encryption key.
        serverless_config (Dict[str, Any], optional): Serverless instance configuration.

    Returns:
        Dict[str, Any]: Response containing the created instance details.
    """
    try:
        client = get_rds_client(region_id)

        request = rds_20140815_models.CreateDBInstanceRequest(
            region_id=region_id,
            engine=engine,
            engine_version=engine_version,
            dbinstance_class=dbinstance_class,
            dbinstance_storage=dbinstance_storage,
            security_iplist=security_ip_list,
            instance_network_type=instance_network_type
        )

        # Add optional parameters
        if zone_id:
            request.zone_id = zone_id
        if pay_type:
            request.pay_type = pay_type
        if instance_charge_type:
            request.instance_charge_type = instance_charge_type
        if system_db_charset:
            request.system_db_charset = system_db_charset
        if dbinstance_net_type:
            request.dbinstance_net_type = dbinstance_net_type
        if category:
            request.category = category
        if dbinstance_storage_type:
            request.dbinstance_storage_type = dbinstance_storage_type
        if vpc_id:
            request.vpc_id = vpc_id
        if vswitch_id:
            request.vswitch_id = vswitch_id
        if private_ip_address:
            request.private_ip_address = private_ip_address
        if client_token:
            request.client_token = client_token
        if resource_group_id:
            request.resource_group_id = resource_group_id
        if dedicated_host_group_id:
            request.dedicated_host_group_id = dedicated_host_group_id
        if tde_status:
            request.tde_status = tde_status
        if encryption_key:
            request.encryption_key = encryption_key
        if serverless_config:
            request.serverless_config = json.dumps(serverless_config)

        response = client.create_dbinstance(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while creating RDS instance: {str(e)}")
        raise e


@mcp.tool()
async def describe_available_zones(
        region_id: str,
        engine: str,
        engine_version: str = None,
        commodity_code: str = None,
        zone_id: str = None,
        dispense_mode: str = None,
        dbinstance_name: str = None,
        category: str = None
) -> Dict[str, Any]:
    """Query available zones for RDS instances.

    Args:
        region_id (str): Region ID.
        engine (str): Database type (MySQL, SQLServer, PostgreSQL, MariaDB).
        engine_version (str, optional): Database version.
            MySQL: 5.5, 5.6, 5.7, 8.0
            SQL Server: 2008r2, 2012, 2014, 2016, 2017, 2019
            PostgreSQL: 10.0, 11.0, 12.0, 13.0, 14.0, 15.0
            MariaDB: 10.3
        commodity_code (str, optional): Commodity code.
            bards: Pay-as-you-go primary instance (China site)
            rds: Subscription primary instance (China site)
            rords: Pay-as-you-go read-only instance (China site)
            rds_rordspre_public_cn: Subscription read-only instance (China site)
            bards_intl: Pay-as-you-go primary instance (International site)
            rds_intl: Subscription primary instance (International site)
            rords_intl: Pay-as-you-go read-only instance (International site)
            rds_rordspre_public_intl: Subscription read-only instance (International site)
            rds_serverless_public_cn: Serverless instance (China site)
            rds_serverless_public_intl: Serverless instance (International site)
        zone_id (str, optional): Zone ID.
        dispense_mode (str, optional): Whether to return zones that support single-zone deployment.
            1: Return (default)
            0: Do not return
        dbinstance_name (str, optional): Primary instance ID. Required when querying read-only instance resources.
        category (str, optional): Instance category.
            Basic: Basic Edition
            HighAvailability: High-availability Edition
            cluster: MySQL Cluster Edition
            AlwaysOn: SQL Server Cluster Edition
            Finance: Enterprise Edition
            serverless_basic: Serverless Basic Edition
            serverless_standard: MySQL Serverless High-availability Edition
            serverless_ha: SQL Server Serverless High-availability Edition

    Returns:
        Dict[str, Any]: Response containing available zones information.
    """
    try:
        # Initialize the client
        client = get_rds_client(region_id)

        # Create request
        request = rds_20140815_models.DescribeAvailableZonesRequest(
            region_id=region_id,
            engine=engine
        )

        # Add optional parameters if provided
        if engine_version:
            request.engine_version = engine_version
        if commodity_code:
            request.commodity_code = commodity_code
        if zone_id:
            request.zone_id = zone_id
        if dispense_mode:
            request.dispense_mode = dispense_mode
        if dbinstance_name:
            request.dbinstance_name = dbinstance_name
        if category:
            request.category = category

        # Make the API request
        response = client.describe_available_zones(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while querying available zones: {str(e)}")
        raise OpenAPIError(f"Failed to query available zones: {str(e)}")


@mcp.tool()
async def describe_vpcs(
        region_id: str,
        vpc_id: str = None,
        vpc_name: str = None,
        resource_group_id: str = None,
        page_number: int = 1,
        page_size: int = 10,
        vpc_owner_id: int = None,
        tags: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Query VPC list.

    Args:
        region_id (str): The region ID of the VPC.
        vpc_id (str, optional): The ID of the VPC. Up to 20 VPC IDs can be specified, separated by commas.
        vpc_name (str, optional): The name of the VPC.
        resource_group_id (str, optional): The resource group ID of the VPC to query.
        page_number (int, optional): The page number of the list. Default: 1.
        page_size (int, optional): The number of entries per page. Maximum value: 50. Default: 10.
        vpc_owner_id (int, optional): The Alibaba Cloud account ID of the VPC owner.
        tags (List[Dict[str, str]], optional): The tags of the resource.

    Returns:
        Dict[str, Any]: The response containing the list of VPCs.
    """
    try:
        # Initialize the client
        client = get_vpc_client(region_id)

        # Create request
        request = vpc_20160428_models.DescribeVpcsRequest(
            region_id=region_id,
            page_number=page_number,
            page_size=page_size
        )

        # Add optional parameters if provided
        if vpc_id:
            request.vpc_id = vpc_id
        if vpc_name:
            request.vpc_name = vpc_name
        if resource_group_id:
            request.resource_group_id = resource_group_id
        if vpc_owner_id:
            request.vpc_owner_id = vpc_owner_id
        if tags:
            request.tag = tags

        # Make the API request
        response = client.describe_vpcs(request)
        return response.to_map()

    except Exception as e:
        logger.error(f"Error occurred while querying VPCs: {str(e)}")
        raise OpenAPIError(f"Failed to query VPCs: {str(e)}")


@mcp.tool()
async def describe_vswitches(
        region_id: str = None,
        vpc_id: str = None,
        vswitch_id: str = None,
        zone_id: str = None,
        vswitch_name: str = None,
        is_default: bool = None,
        resource_group_id: str = None,
        page_number: int = 1,
        page_size: int = 10,
        vswitch_owner_id: int = None,
        tags: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Query VSwitch list.

    Args:
        region_id (str, optional): The region ID of the VSwitch. At least one of region_id or vpc_id must be specified.
        vpc_id (str, optional): The ID of the VPC to which the VSwitch belongs. At least one of region_id or vpc_id must be specified.
        vswitch_id (str, optional): The ID of the VSwitch to query.
        zone_id (str, optional): The zone ID of the VSwitch.
        vswitch_name (str, optional): The name of the VSwitch.
        resource_group_id (str, optional): The resource group ID of the VSwitch.
        page_number (int, optional): The page number of the list. Default: 1.
        page_size (int, optional): The number of entries per page. Maximum value: 50. Default: 10.
        vswitch_owner_id (int, optional): The Alibaba Cloud account ID of the VSwitch owner.
        tags (List[Dict[str, str]], optional): The tags of the resource.

    Returns:
        Dict[str, Any]: The response containing the list of VSwitches.
    """
    try:
        # Initialize the client
        if not region_id and not vpc_id:
            raise OpenAPIError("At least one of region_id or vpc_id must be specified")

        client = get_vpc_client(region_id)

        # Create request
        request = vpc_20160428_models.DescribeVSwitchesRequest(
            page_number=page_number,
            page_size=page_size
        )

        # Add optional parameters if provided
        if vpc_id:
            request.vpc_id = vpc_id
        if vswitch_id:
            request.vswitch_id = vswitch_id
        if zone_id:
            request.zone_id = zone_id
        if vswitch_name:
            request.vswitch_name = vswitch_name
        if is_default is not None:
            request.is_default = is_default
        if resource_group_id:
            request.resource_group_id = resource_group_id
        if vswitch_owner_id:
            request.vswitch_owner_id = vswitch_owner_id
        if tags:
            request.tag = tags

        # Make the API request
        response = client.describe_vswitches(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while querying VSwitches: {str(e)}")
        raise OpenAPIError(f"Failed to query VSwitches: {str(e)}")


@mcp.tool()
async def describe_slow_log_records(
        region_id: str,
        dbinstance_id: str,
        start_time: str,
        end_time: str,
        sqlhash: str = None,
        db_name: str = None,
        page_size: int = 30,
        page_number: int = 1,
        node_id: str = None
) -> Dict[str, Any]:
    """Query slow log records for an RDS instance.

    Args:
        region_id (str): The region ID of the RDS instance.
        dbinstance_id (str): The ID of the RDS instance.
        start_time (str): Start time in format: yyyy-MM-dd HH:mm.
            Cannot be earlier than 30 days before the current time.
        end_time (str): End time in format: yyyy-MM-dd HH:mm.
            Must be later than the start time.
        sqlhash (str, optional): The unique identifier of the SQL statement in slow log statistics.
            Used to get slow log details for a specific SQL statement.
        db_name (str, optional): The name of the database.
        page_size (int, optional): Number of records per page. Range: 30-100. Default: 30.
        page_number (int, optional): Page number. Must be greater than 0 and not exceed Integer max value. Default: 1.
        node_id (str, optional): Node ID. Only applicable to cluster instances.
            If not specified, logs from the primary node are returned by default.

    Returns:
        Dict[str, Any]: The response containing slow log records.
    """
    try:
        # Initialize the client
        client = get_rds_client(region_id)
        start_time = transform_to_datetime(start_time)
        end_time = transform_to_datetime(end_time)
        # Create request
        request = rds_20140815_models.DescribeSlowLogRecordsRequest(
            dbinstance_id=dbinstance_id,
            start_time=transform_to_iso_8601(start_time, "minutes"),
            end_time=transform_to_iso_8601(end_time, "minutes"),
            page_size=page_size,
            page_number=page_number
        )

        # Add optional parameters if provided
        if sqlhash:
            request.sqlhash = sqlhash
        if db_name:
            request.db_name = db_name
        if node_id:
            request.node_id = node_id

        # Make the API request
        response = client.describe_slow_log_records(request)
        return response.body.to_map()

    except Exception as e:
        logger.error(f"Error occurred while querying slow log records: {str(e)}")
        raise OpenAPIError(f"Failed to query slow log records: {str(e)}")


@mcp.tool()
async def describe_error_logs(
        region_id: str,
        db_instance_id: str,
        start_time: str,
        end_time: str,
        page_size: int = 30,
        page_number: int = 1
) -> Dict[str, Any]:
    """
    Query error logs of an RDS instance.
    Args:
        region_id (str): The region ID of the RDS instance.
        db_instance_id (str): The ID of the RDS instance.
        start_time (str): The start time of the query. Format: yyyy-MM-dd HH:mm.
        end_time (str): The end time of the query. Format: yyyy-MM-dd HH:mm.
        page_size (int): The number of records per page. Range: 30~100. Default: 30.
        page_number (int): The page number. Default: 1.
    Returns:
        Dict[str, Any]: A dictionary containing error log information
    """
    try:
        start_time = transform_to_datetime(start_time)
        end_time = transform_to_datetime(end_time)
        client = get_rds_client(region_id)
        request = rds_20140815_models.DescribeErrorLogsRequest(
            dbinstance_id=db_instance_id,
            start_time=transform_to_iso_8601(start_time, "minutes"),
            end_time=transform_to_iso_8601(end_time, "minutes"),
            page_size=page_size,
            page_number=page_number
        )
        response = await client.describe_error_logs_async(request)
        return {
            "Logs": "\n".join([log.error_info for log in response.body.items.error_log]),
            "PageNumber": response.body.page_number,
            "PageRecordCount": response.body.page_record_count,
            "TotalRecordCount": response.body.total_record_count
        }
    except Exception as e:
        logger.error(f"Failed to describe error logs: {str(e)}")
        raise OpenAPIError(f"Failed to describe error logs: {str(e)}")


@mcp.tool()
async def describe_db_instance_net_info(
        region_id: str,
        db_instance_ids: list[str]
) -> list[dict]:
    """
    Batch retrieves network configuration details for multiple RDS instances.
    Args:
        region_id (str): The region ID of the RDS instance.
        db_instance_ids (list[str]): List of DB instance identifiers (e.g., ["rm-uf6wjk5****", "db-instance-01"])
    Returns:
        list[dict]: A list of dictionaries containing network configuration details for each instance.
    """
    try:
        client = get_rds_client(region_id)
        db_instance_net_infos = []
        for db_instance_id in db_instance_ids:
            request = rds_20140815_models.DescribeDBInstanceNetInfoRequest(
                dbinstance_id=db_instance_id
            )
            response = await client.describe_dbinstance_net_info_async(request)
            db_instance_net_infos.append(response.body.to_map())
        return db_instance_net_infos
    except Exception as e:
        raise e


@mcp.tool()
async def describe_db_instance_ip_allowlist(
        region_id: str,
        db_instance_ids: list[str]
) -> list[dict]:
    """
    Batch retrieves IP allowlist configurations for multiple RDS instances.
    Args:
        region_id (str): The region ID of the RDS instance.
        db_instance_ids (list[str]): List of DB instance identifiers (e.g., ["rm-uf6wjk5****", "db-instance-01"])
    Returns:
        list[dict]: A list of dictionaries containing network configuration details for each instance.
    """
    try:
        client = get_rds_client(region_id)
        db_instance_ip_allowlist = []
        for db_instance_id in db_instance_ids:
            request = rds_20140815_models.DescribeDBInstanceIPArrayListRequest(
                dbinstance_id=db_instance_id
            )
            response = await client.describe_dbinstance_iparray_list_async(request)
            db_instance_ip_allowlist.append(response.body.to_map())
        return db_instance_ip_allowlist
    except Exception as e:
        raise e


@mcp.tool()
async def describe_db_instance_databases(
        region_id: str,
        db_instance_ids: list[str]
) -> list[dict]:
    """
    Batch retrieves database information for multiple RDS instances.
    Args:
        region_id (str): The region ID of the RDS instance.
        db_instance_ids (list[str]): List of DB instance identifiers (e.g., ["rm-uf6wjk5****", "db-instance-01"])
    Returns:
        list[dict]: A list of dictionaries containing database information for each instance.
    """
    try:
        client = get_rds_client(region_id)
        db_instance_databases = []
        for db_instance_id in db_instance_ids:
            request = rds_20140815_models.DescribeDatabasesRequest(
                dbinstance_id=db_instance_id
            )
            response = await client.describe_databases_async(request)
            db_instance_databases.append(response.body.to_map())
        return db_instance_databases
    except Exception as e:
        raise e


@mcp.tool()
async def describe_db_instance_accounts(
        region_id: str,
        db_instance_ids: list[str]
) -> list[dict]:
    """
    Batch retrieves account information for multiple RDS instances.
    Args:
        region_id (str): The region ID of the RDS instance.
        db_instance_ids (list[str]): List of DB instance identifiers (e.g., ["rm-uf6wjk5****", "db-instance-01"])
    Returns:
        list[dict]: A list of dictionaries containing account information for each instance.
    """
    try:
        client = get_rds_client(region_id)
        db_instance_accounts = []
        for db_instance_id in db_instance_ids:
            request = rds_20140815_models.DescribeAccountsRequest(
                dbinstance_id=db_instance_id
            )
            response = await client.describe_accounts_async(request)
            db_instance_accounts.append(response.body.to_map())
        return db_instance_accounts
    except Exception as e:
        raise e


@mcp.tool()
async def get_current_time() -> Dict[str, Any]:
    """Get the current time.

    Returns:
        Dict[str, Any]: The response containing the current time.
    """
    try:
        # Get the current time
        current_time = datetime.now()

        # Format the current time as a string
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Return the response
        return {
            "current_time": formatted_time
        }
    except Exception as e:
        logger.error(f"Error occurred while getting the current time: {str(e)}")
        raise Exception(f"Failed to get the current time: {str(e)}")


if __name__ == '__main__':
    # Initialize and run the server
    mcp.run(transport=os.getenv('SERVER_TRANSPORT', 'stdio'))
