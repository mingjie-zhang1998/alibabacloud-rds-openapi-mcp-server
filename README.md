# Alibaba Cloud RDS OpenAPI MCP Server
MCP server for RDS Services via OPENAPI
## Prerequisites
1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.12`
3. Alibaba Cloud credentials with access to Alibaba Cloud RDS services

## Configuration
### Using Local File
#### Download
Download from Github
```shell
git clone https://github.com/aliyun/alibabacloud-rds-openapi-mcp-server.git
```
#### MCP Integration
Add the following configuration to the MCP client configuration file:
```json
"mcpServers": {
  "rds-openapi-mcp-server": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/alibabacloud-rds-openapi-mcp-server/src/rds_openapi_mcp_server",
      "run",
      "server.py"
    ],
    "env": {
      "ALIBABA_CLOUD_ACCESS_KEY_ID": "access_id",
      "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "access_key"
    }
  }
}
```

## Components
### Tools
* `describe_db_instances`: Queries instances.
* `describe_db_instance_attribute`: Queries the details of an instance.
* `describe_db_instance_metrics`: Queries the performance data、error log and sql reports of an instance.
* `modify_parameter`: Modify RDS instance parameters.
* `modify_db_instance_spec`: Modify RDS instance specifications.
* `describe_available_classes`: Query available instance classes and storage ranges.
* `create_db_instance`: Create an RDS instance.
* `describe_available_zones`: Query available zones for RDS instances.
* `describe_vpcs`: Query VPC list.
* `describe_vswitches`: Query VSwitch list.
* `describe_slow_log_records`: Query slow log records for an RDS instance.

### Resources
None at this time

### Prompts
None at this time