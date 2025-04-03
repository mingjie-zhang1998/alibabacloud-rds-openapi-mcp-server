# Alibaba Cloud RDS OpenAPI MCP Server
MCP server for RDS Services via OPENAPI

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

### Resources
None at this time

### Prompts
None at this time