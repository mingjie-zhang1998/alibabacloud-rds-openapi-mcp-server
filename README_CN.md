<h1 align="center">
  <a>
    <img src="https://github.com/aliyun/alibabacloud-rds-openapi-mcp-server/blob/main/assets/rds_mcp.png?raw=true" width="541" height="360.5" alt="banner" /><br>
  </a>
</h1>
<p align="center"><a href="./README.md">English</a> | 中文<br></p>

# 阿里云RDS OpenAPI MCP 服务
RDS OpenAPI MCP服务。
## 前提条件
1. 从[Astral](https://docs.astral.sh/uv/getting-started/installation/)或[GitHub README](https://github.com/astral-sh/uv#installation)安装`uv`
2. 使用`uv python install 3.12`安装Python
3. 具有阿里云RDS服务访问权限的账号凭证

## 快速开始
### 下载
从Github克隆仓库
```shell
git clone https://github.com/aliyun/alibabacloud-rds-openapi-mcp-server.git
```

### 使用[cherry-studio](https://github.com/CherryHQ/cherry-studio)（推荐）
根据[Cherry-Studio文档](https://docs.cherry-ai.com/advanced-basic/mcp/install)安装MCP环境后配置使用RDS MCP。 MCP配置文件格式如下：
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

### 使用Cline
设置环境变量并运行MCP服务
```shell
# 设置环境变量
export SERVER_TRANSPORT=sse;
export ALIBABA_CLOUD_ACCESS_KEY_ID=$your_access_id;  # 替换为你的access_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=$your_access_key;  # 替换为你的access_key

# 启动MCP服务
uv --directory alibabacloud-rds-openapi-mcp-server/src/rds_openapi_mcp_server run server.py
```
成功启动后会看到以下输出：
```shell
INFO:     Started server process [91594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
然后在Cline中配置：
```shell
remote_server = "http://127.0.0.1:8000/sse";
```

### 使用Claude
在MCP客户端配置文件中添加：
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

## 功能组件
### 工具集
* `create_db_instance`: 创建RDS实例
* `describe_db_instances`: 查询实例列表
* `describe_db_instance_attribute`: 查询实例详情
* `describe_db_instance_metrics`: 查询实例性能数据、错误日志和SQL报告
* `describe_available_classes`: 查询可用实例规格和存储范围
* `describe_available_zones`: 查询RDS可用区
* `describe_vpcs`: 查询VPC列表
* `describe_vswitches`: 查询虚拟交换机列表
* `describe_slow_log_records`: 查询RDS慢日志记录
* `modify_parameter`: 修改RDS实例参数
* `modify_db_instance_spec`: 调整RDS实例规格

### 资源
当前暂无资源

### 提示模板
当前暂无提示模板

## 贡献指南
欢迎贡献代码！请提交Pull Request：
1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交修改（`git commit -m '添加新特性'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 发起Pull Request

## 许可证
本项目采用Apache 2.0许可证

