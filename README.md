# Alibaba Cloud RDS OpenAPI MCP Server
MCP server for RDS Services via OPENAPI
## Prerequisites
1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.12`
3. Alibaba Cloud credentials with access to Alibaba Cloud RDS services

## Quick Start
### Download
Download from Github
```shell
git clone https://github.com/aliyun/alibabacloud-rds-openapi-mcp-server.git
```
### Using Cline
Set you env and run mcp server.
```shell
# set env
export SERVER_TRANSPORT=sse;
export ALIBABA_CLOUD_ACCESS_KEY_ID=$you_access_id;
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=$you_access_key;

# run mcp server
uv --directory alibabacloud-rds-openapi-mcp-server/src/rds_openapi_mcp_server run server.py
```
After run mcp server, you will see the following output:
```shell
INFO:     Started server process [91594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
And then configure the Cline.
```shell
remote_server = "http://127.0.0.1:8000/sse";
```


### Using Claude
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
* `create_db_instance`: Create an RDS instance.
* `describe_db_instances`: Queries instances.
* `describe_db_instance_attribute`: Queries the details of an instance.
* `describe_db_instance_metrics`: Queries the performance data、error log and sql reports of an instance.
* `describe_available_classes`: Query available instance classes and storage ranges.
* `describe_available_zones`: Query available zones for RDS instances.
* `describe_vpcs`: Query VPC list.
* `describe_vswitches`: Query VSwitch list.
* `describe_slow_log_records`: Query slow log records for an RDS instance.
* `modify_parameter`: Modify RDS instance parameters.
* `modify_db_instance_spec`: Modify RDS instance specifications.

### Resources
None at this time

### Prompts
None at this time

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the Apache 2.0 License.
