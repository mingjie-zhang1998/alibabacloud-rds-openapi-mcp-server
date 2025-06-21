# -*- coding: utf-8 -*-
"""Provides core functionalities for the "rds_custom" MCP toolset.

This module contains the engine-agnostic logic and serves as the **required
base dependency** for all engine-specific toolsets. It can also be loaded
stand-alone for basic operations.

Toolsets are loaded at runtime via the `--toolsets` command-line argument
or a corresponding environment variable.

Command-Line Usage:
-------------------
1.  **Base Usage Only:**
    To load only the base functionalities, specify `rds_custom` by itself.

2.  **Single-Engine Usage:**
    To use tools for a specific engine (e.g., SQL Server), you MUST include
    **both** the base toolset `rds_custom` AND the engine-specific toolset
    `rds_custom_mssql` in the list, separated by a comma.

Command-Line Examples:
----------------------
# Scenario 1: Basic usage with only the base toolset
# python server.py --toolsets rds_custom

# Scenario 2: Usage for SQL Server
# python your_server.py --toolsets rds_custom,rds_custom_mssql
"""

import logging
from typing import Dict, Any, Optional, List
from .tool_registry import tool
import alibabacloud_rds20140815.models as RdsApiModels
from .aliyun_openapi_gateway import AliyunServiceGateway


logger = logging.getLogger(__name__)

RDS_CUSTOM_GROUP_NAME = 'rds_custom'

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instances(region_id: str, instance_id: str|None) -> Dict[str, Any]:
    """
    describe rds custom instances.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_id: The ID of a specific instance. If omitted, all instances in the region are returned.

    Returns:
        dict[str, Any]: The response containing instance metadata.
    """
    request = RdsApiModels.DescribeRCInstancesRequest(
        region_id=region_id,
        instance_id=instance_id
    )
    rds_client = AliyunServiceGateway(region_id).rds()
    return rds_client.describe_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def describe_rc_instance_attribute(region_id: str,instance_id: str) -> Dict[str, Any]:
    """
    describe a single rds custom instance's details.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.

    Returns:
        dict[str, Any]: The response containing the instance details.
    """
    request = RdsApiModels.DescribeRCInstanceAttributeRequest(
        region_id=region_id,
        instance_id=instance_id
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_attribute_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def resize_rc_instance_disk(
    region_id: str,
    instance_id: str,
    new_size: int,
    disk_id: str,
    auto_pay: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    resize a specific rds custom instance's disk.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        new_size: The target size of the disk in GiB.
        disk_id: The ID of the cloud disk.
        auto_pay: Specifies whether to enable automatic payment. Default is false.
        dry_run: Specifies whether to perform a dry run. Default is false.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.ResizeRCInstanceDiskRequest(
        region_id=region_id,
        instance_id=instance_id,
        new_size=new_size,
        disk_id=disk_id,
        auto_pay=auto_pay,
        dry_run=dry_run,
        type='online'
    )
    return AliyunServiceGateway(region_id).rds().resize_rcinstance_disk_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def describe_rc_instance_vnc_url(
    region_id: str,
    instance_id: str,
    db_type: str
) -> Dict[str, Any]:
    """
    describe the vnc login url for a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance.
        db_type: The database type, e.g., 'mysql' or 'mssql'.

    Returns:
        dict[str, Any]: The response containing the VNC login URL.
    """
    request = RdsApiModels.DescribeRCInstanceVncUrlRequest(
        region_id=region_id,
        instance_id=instance_id,
        db_type=db_type
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_vnc_url_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def modify_rc_instance_attribute(
    region_id: str,
    instance_id: str,
    password: Optional[str] = None,
    reboot: Optional[bool] = None,
    host_name: Optional[str] = None,
    security_group_id: Optional[str] = None,
    deletion_protection: Optional[bool] = None
) -> Dict[str, Any]:
    """
    modify attributes of a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance to modify.
        password: The new password for the instance.
        reboot: Specifies whether to restart the instance after modification.
        host_name: The new hostname for the instance.
        security_group_id: The ID of the new security group for the instance.
        deletion_protection: Specifies whether to enable the deletion protection feature.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.ModifyRCInstanceAttributeRequest(
        region_id=region_id,
        instance_id=instance_id,
        password=password,
        reboot=reboot,
        host_name=host_name,
        security_group_id=security_group_id,
        deletion_protection=deletion_protection
    )
    return AliyunServiceGateway(region_id).rds().modify_rcinstance_attribute_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def modify_rc_instance_description(
    region_id: str,
    instance_id: str,
    instance_description: str
) -> Dict[str, Any]:
    """
    modify the description of a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to modify.
        instance_description: The new description for the instance.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """

    request = RdsApiModels.ModifyRCInstanceDescriptionRequest(
        region_id=region_id,
        instance_id=instance_id,
        instance_description=instance_description
    )
    return AliyunServiceGateway(region_id).rds().modify_rcinstance_description_with_options(request)