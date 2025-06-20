import importlib
import pkgutil
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .toolsets import ToolsetMCP

# Global MCP instance for tool registration
mcp_instance: Optional["ToolsetMCP"] = None


def tool(*args, **kwargs):
    """
    Proxy decorator that delegates to the actual decorator on the MCP instance.
    """
    if mcp_instance is None:
        raise RuntimeError("ToolsetMCP instance has not been set in tool_registry.")
    return mcp_instance.tool(*args, **kwargs)


def load_groups(mcp: "ToolsetMCP") -> None:
    """
    Auto-discover and import all modules in the current package to trigger tool registration.
    This function finds all modules at the same level as the current file and imports them.
    """
    global mcp_instance
    mcp_instance = mcp

    package_path = [os.path.dirname(os.path.abspath(__file__))]
    package_name = __name__.rpartition('.')[0] if '.' in __name__ else __name__

    for _, module_name, _ in pkgutil.iter_modules(package_path, package_name + '.'):
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Failed to load tool module {module_name}: {e}")