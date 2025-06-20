import importlib
import sys
from pathlib import Path
import types

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Provide a minimal stub for the ``mcp`` package used during tests.
fastmcp_stub = types.ModuleType("mcp.server.fastmcp")

class FastMCP:
    def __init__(self, *args, **kwargs):
        self._tools = []

    @staticmethod
    def tool(mcp, *args, **kwargs):
        def decorator(func):
            mcp._tools.append(func)
            return func
        return decorator

fastmcp_stub.FastMCP = FastMCP
server_pkg_stub = types.ModuleType("mcp.server")
server_pkg_stub.fastmcp = fastmcp_stub
mcp_stub = types.ModuleType("mcp")
mcp_stub.server = server_pkg_stub
sys.modules.setdefault("mcp", mcp_stub)
sys.modules.setdefault("mcp.server", server_pkg_stub)
sys.modules.setdefault("mcp.server.fastmcp", fastmcp_stub)

from alibabacloud_rds_openapi_mcp_server.toolsets.toolsets import (
    ToolsetMCP,
    initialize_toolsets,
)


def make_server_module():
    """Create a dummy server module with two tools registered."""
    server = types.ModuleType("alibabacloud_rds_openapi_mcp_server.server")
    server.mcp = ToolsetMCP("dummy")
    server.toolset_manager = server.mcp.manager

    @server.mcp.tool()
    async def describe_db_instances():
        pass

    @server.mcp.tool()
    async def describe_db_instance_attribute():
        pass

    server.describe_db_instances = describe_db_instances
    server.describe_db_instance_attribute = describe_db_instance_attribute

    sys.modules["alibabacloud_rds_openapi_mcp_server.server"] = server
    return server


def make_rds_custom(server):
    module = types.ModuleType(
        "alibabacloud_rds_openapi_mcp_server.toolsets.rds_custom"
    )

    @server.mcp.tool(group="rds_custom")
    async def custom_echo(text: str):
        return text

    module.custom_echo = custom_echo
    sys.modules[
        "alibabacloud_rds_openapi_mcp_server.toolsets.rds_custom"
    ] = module
    return module


@pytest.fixture(autouse=True)
def dummy_env(monkeypatch):
    server = make_server_module()
    make_rds_custom(server)
    yield server


def test_load_groups_should_assign_tools_to_correct_groups_when_called(dummy_env):
    server = dummy_env
    from alibabacloud_rds_openapi_mcp_server.toolsets.tool_registry import load_groups

    load_groups(server.mcp)

    groups = server.toolset_manager.groups
    assert "rds" in groups
    assert server.describe_db_instances in [i.func for i in groups["rds"]]
    assert server.describe_db_instance_attribute in [i.func for i in groups["rds"]]
    assert "rds_custom" in groups
    assert any(i.func.__name__ == "custom_echo" for i in groups["rds_custom"])


def test_initialize_toolsets_should_enable_default_group_when_toolsets_none(dummy_env):
    server = dummy_env
    initialize_toolsets(None, server.mcp)
    assert server.toolset_manager.enabled == {"rds"}


def test_manager_should_report_enabled_groups_and_tools_when_queried(dummy_env):
    server = dummy_env
    from alibabacloud_rds_openapi_mcp_server.toolsets.tool_registry import load_groups

    load_groups(server.mcp)
    server.toolset_manager.enable("rds", "rds_custom")

    assert set(server.toolset_manager.registered_tool_groups()) >= {"rds", "rds_custom"}
    assert set(server.toolset_manager.enabled_tool_groups()) == {"rds", "rds_custom"}
    enabled = server.toolset_manager.enabled_tools()
    assert "rds" in enabled and server.describe_db_instances in enabled["rds"]
    assert "rds_custom" in enabled and any(
        f.__name__ == "custom_echo" for f in enabled["rds_custom"]
    )

def test_set_group_should_move_tool_to_new_group_when_called(dummy_env):
    manager = dummy_env.toolset_manager

    def new_tool():
        pass

    manager.add_tool(new_tool)
    manager.set_group(new_tool, "new_group")

    assert "new_group" in manager.groups
    assert new_tool in [i.func for i in manager.groups["new_group"]]
    assert all(i.func != new_tool for i in manager.groups["rds"])


def test_register_enabled_should_register_only_tools_from_enabled_groups(dummy_env):
    manager = dummy_env.toolset_manager

    async def tool_a():
        pass

    async def tool_b():
        pass

    manager.add_tool(tool_a, group="group_a")
    manager.add_tool(tool_b, group="group_b")

    manager.enable("group_a")
    manager.register_enabled(dummy_env.mcp)

    assert tool_a in dummy_env.mcp._tools
    assert tool_b not in dummy_env.mcp._tools


def test_initialize_toolsets_should_raise_when_group_invalid(dummy_env):
    with pytest.raises(ValueError):
        initialize_toolsets("invalid_group", dummy_env.mcp)
