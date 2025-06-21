# -*- coding: utf-8 -*-
import logging
from typing import Dict, Any, Optional, List
from .tool_registry import tool
import alibabacloud_rds20140815.models as RdsApiModels
from .aliyun_openapi_gateway import AliyunServiceGateway

logger = logging.getLogger(__name__)

RDS_CUSTOM_GROUP_NAME = 'rds_mssql_custom'

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instances(region_id: str, db_instance_id: str|None) -> Dict[str, Any]:
    """
    describe rds custom instances.

    Args:
        region_id: The region ID of the RDS Custom instances.
        db_instance_id: The ID of a specific instance. If omitted, all instances in the region are returned.

    Returns:
        dict[str, Any]: The response containing instance metadata.
    """
    request = RdsApiModels.DescribeRCInstancesRequest(
        region_id=region_id,
        instance_id=db_instance_id
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
def describe_rc_instance_ip_address(
    region_id: str,
    instance_id: str,
    ddos_region_id: str,
    instance_type: str = 'ecs',
    resource_type: str = 'ecs',
    ddos_status: Optional[str] = None,
    instance_ip: Optional[str] = None,
    current_page: Optional[int] = None,
    page_size: Optional[int] = None,
    instance_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe the ddos protection details for an rds custom instance.
    Args:
        region_id: The region ID where the Custom instance is located.
        instance_id: The ID of the Custom instance.
        ddos_region_id: The region ID of the public IP asset.
        instance_type: The instance type of the public IP asset, fixed value 'ecs'.
        resource_type: The resource type, fixed value 'ecs'.
        ddos_status: The DDoS protection status of the public IP asset.
        instance_ip: The IP address of the public IP asset to query.
        current_page: The page number of the results to display.
        page_size: The number of instances per page.
        instance_name: The name of the Custom instance.

    Returns:
        dict[str, Any]: The response containing the DDoS protection details.
    """
    request = RdsApiModels.DescribeRCInstanceIpAddressRequest(
        region_id=region_id,
        instance_id=instance_id,
        ddos_region_id=ddos_region_id,
        instance_type=instance_type,
        resource_type=resource_type,
        ddos_status=ddos_status,
        instance_ip=instance_ip,
        current_page=current_page,
        page_size=page_size,
        instance_name=instance_name
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_ip_address_with_options(request)

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
def stop_rc_instances(
    region_id: str,
    instance_ids: List[str],
    force_stop: bool = False,
    batch_optimization: Optional[str] = None
) -> Dict[str, Any]:
    """
    stop one or more rds custom instances in batch.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_ids: A list of instance IDs to be stopped.
        force_stop: Specifies whether to force stop the instances. Default is false.
        batch_optimization: The batch operation mode.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.StopRCInstancesRequest(
        region_id=region_id,
        instance_ids=instance_ids,
        force_stop=force_stop,
        batch_optimization=batch_optimization
    )
    return AliyunServiceGateway(region_id).rds().stop_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def start_rc_instances(
    region_id: str,
    instance_ids: List[str],
    batch_optimization: Optional[str] = None
) -> Dict[str, Any]:
    """
    start one or more rds custom instances in batch.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_ids: A list of instance IDs to be started.
        batch_optimization: The batch operation mode.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.StartRCInstancesRequest(
        region_id=region_id,
        instance_ids=instance_ids,
        batch_optimization=batch_optimization
    )
    return AliyunServiceGateway(region_id).rds().start_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def reboot_rc_instance(
    region_id: str,
    instance_id: str,
    force_stop: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    reboot a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to reboot.
        force_stop: Specifies whether to force shutdown before rebooting. Default is false.
        dry_run: Specifies whether to perform a dry run only. Default is false.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.RebootRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        force_stop=force_stop,
        dry_run=dry_run
    )
    return AliyunServiceGateway(region_id).rds().reboot_rcinstance_with_options(request)

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

@tool(group=RDS_CUSTOM_GROUP_NAME)
def describe_rc_image_list(
    region_id: str,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    type: Optional[str] = None,
    architecture: Optional[str] = None,
    image_id: Optional[str] = None,
    image_name: Optional[str] = None,
    instance_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe the list of custom images for creating rds custom instances.

    Args:
        region_id: The region ID to query for images.
        page_number: The page number of the results.
        page_size: The number of records per page.
        type: The image type, currently only 'self' is supported.
        architecture: The system architecture of the image, e.g., 'x86_64'.
        image_id: The ID of a specific image to query.
        image_name: The name of a specific image to query.
        instance_type: The instance type to query usable images for.

    Returns:
        dict[str, Any]: The response containing the list of custom images.
    """
    request = RdsApiModels.DescribeRCImageListRequest(
        region_id=region_id,
        page_number=page_number,
        page_size=page_size,
        type=type,
        architecture=architecture,
        image_id=image_id,
        image_name=image_name,
        instance_type=instance_type
    )

    return AliyunServiceGateway(region_id).rds().describe_rcimage_list_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def describe_rc_metric_list(
    region_id: str,
    instance_id: str,
    metric_name: str,
    start_time: str,
    end_time: str,
    period: Optional[str] = None,
    length: Optional[str] = None,
    next_token: Optional[str] = None,
    dimensions: Optional[str] = None,
    express: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe monitoring data for a specific metric of an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to query.
        metric_name: The metric to be monitored, e.g., 'CPUUtilization'.
        start_time: The start time of the query, format 'YYYY-MM-DD HH:MM:SS'.
        end_time: The end time of the query, format 'YYYY-MM-DD HH:MM:SS'.
        period: The statistical period of the monitoring data in seconds.
        length: The number of entries to return on each page.
        next_token: The pagination token.
        dimensions: The dimensions to query data for multiple resources in batch.
        express: A reserved parameter.

    Returns:
        dict[str, Any]: The response containing the list of monitoring data.
    """
    request = RdsApiModels.DescribeRCMetricListRequest(
        region_id=region_id,
        instance_id=instance_id,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time,
        period=period,
        length=length,
        next_token=next_token,
        dimensions=dimensions,
        express=express
    )

    return AliyunServiceGateway(region_id).rds().describe_rcmetric_list_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def sync_rc_security_group(
    region_id: str,
    instance_id: str,
    security_group_id: str
) -> Dict[str, Any]:
    """
    synchronize the security group rules for an rds sql server custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        security_group_id: The ID of the security group.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.SyncRCSecurityGroupRequest(
        region_id=region_id,
        instance_id=instance_id,
        security_group_id=security_group_id
    )

    return AliyunServiceGateway(region_id).rds().sync_rcsecurity_group_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def associate_eip_address_with_rc_instance(
    region_id: str,
    instance_id: str,
    allocation_id: str
) -> Dict[str, Any]:
    """
    associate an elastic ip address (eip) with an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        allocation_id: The ID of the Elastic IP Address.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.AssociateEipAddressWithRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        allocation_id=allocation_id
    )

    return AliyunServiceGateway(region_id).rds().associate_eip_address_with_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def unassociate_eip_address_with_rc_instance(
    region_id: str,
    instance_id: str,
    allocation_id: str
) -> Dict[str, Any]:
    """
    unassociate an elastic ip address (eip) from an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        allocation_id: The ID of the Elastic IP Address to unassociate.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.UnassociateEipAddressWithRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        allocation_id=allocation_id
    )

    return AliyunServiceGateway(region_id).rds().unassociate_eip_address_with_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
def describe_rc_instance_ddos_count(
    region_id: str,
    ddos_region_id: str,
    instance_type: str = 'ecs'
) -> Dict[str, Any]:
    """
    describe the count of ddos attacks on rds custom instances.

    Args:
        region_id: The region ID where the Custom instance is located.
        ddos_region_id: The region ID of the public IP asset to query.
        instance_type: The instance type of the public IP asset, fixed value 'ecs'.

    Returns:
        dict[str, Any]: The response containing the count of ddos attacks.
    """
    request = RdsApiModels.DescribeRCInstanceDdosCountRequest(
        region_id=region_id,
        ddos_region_id=ddos_region_id,
        instance_type=instance_type
    )

    return AliyunServiceGateway(region_id).rds().describe_rcinstance_ddos_count_with_options(request)