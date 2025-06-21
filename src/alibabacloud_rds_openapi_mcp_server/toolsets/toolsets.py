# -*- coding: utf-8 -*-
"""Utility classes to manage groups of MCP tools."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

from mcp.server.fastmcp import FastMCP
import os

DEFAULT_TOOL_GROUP = 'rds'

@dataclass
class _ToolInfo:
    func: Callable
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    group: str


class ToolsetManager:
    """Manage tool groups and register them on demand."""

    def __init__(self) -> None:
        # Mapping of tool function to its metadata for easy regrouping
        self._tools: Dict[Callable, _ToolInfo] = {}
        self.groups: Dict[str, List[_ToolInfo]] = {}
        self.enabled: set[str] = set()

    def add_tool(
        self,
        func: Callable,
        group: str = DEFAULT_TOOL_GROUP,
        args: Tuple[Any, ...] | None = None,
        kwargs: Dict[str, Any] | None = None,
    ) -> None:
        """Add a tool to a group without registering it."""
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        info = self._tools.get(func)
        if info:
            # remove from previous group list if re-added
            if info.group in self.groups:
                self.groups[info.group] = [i for i in self.groups[info.group] if i.func != func]
        info = _ToolInfo(func=func, args=args, kwargs=kwargs, group=group)
        self._tools[func] = info
        self.groups.setdefault(group, []).append(info)

    def set_group(self, func: Callable, group: str) -> None:
        """Set or Move a registered tool to a different group."""
        info = self._tools.get(func)
        if info is None:
            # tool not registered yet; add directly
            self.add_tool(func, group=group)
            return
        if info.group == group:
            return
        # remove from old group
        old_group = info.group
        if old_group in self.groups:
            self.groups[old_group] = [i for i in self.groups[old_group] if i.func != func]
        info.group = group
        self.groups.setdefault(group, []).append(info)

    def enable(self, *groups: str) -> None:
        """Enable one or more groups."""
        for g in groups:
            self.enabled.add(g)

    def registered_tool_groups(self) -> List[str]:
        """Return a list of all groups that have tools registered."""
        return list(self.groups.keys())

    def enabled_tool_groups(self) -> List[str]:
        """Return a list of currently enabled groups."""
        return list(self.enabled)

    def enabled_tools(self) -> Dict[str, List[Callable]]:
        """Return mapping of enabled group name to its tools."""
        result: Dict[str, List[Callable]] = {}
        for name in self.enabled:
            result[name] = [info.func for info in self.groups.get(name, [])]
        return result

    def register_enabled(self, mcp: FastMCP) -> None:
        """Register only tools from enabled groups with MCP."""
        for info in self._tools.values():
            if info.group in self.enabled:
                FastMCP.tool(mcp, *info.args, **info.kwargs)(info.func)



class ToolsetMCP(FastMCP):
    """FastMCP variant that stores tools in ``ToolsetManager``."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.manager = ToolsetManager()
        super().__init__(*args, **kwargs)

    '''
    Decorate a tool and store it for later registration.

    This method overrides the mcp.tool() registration mechanism.
    All tools not explicitly assigned to specific groups in tool_registry.py's
    load_groups function will be automatically categorized into the
    "rds" group. This ensures that when launching without toolsets
    parameters, these default tools are automatically loaded.

    Note:
        - Tools assigned to "rds" group are loaded when no specific toolsets are specified
        - This provides fallback behavior for uncategorized tools
    '''
    def tool(self, *dargs: Any, group: str = DEFAULT_TOOL_GROUP, **dkwargs: Any):
        if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
            func = dargs[0]
            self.manager.add_tool(func, group=group, args=(), kwargs={})
            return func

        def decorator(func: Callable):
            self.manager.add_tool(func, group=group, args=dargs, kwargs=dkwargs)
            return func

        return decorator

    def register_enabled_tools(self) -> None:
        self.manager.register_enabled(self)


def initialize_toolsets(
    toolsets: list[str] | str | None,
    mcp_server: FastMCP
) -> None:
    """
    Load tool groups and register only the selected group into the MCP instance.
    Set environment variable TOOLSET_DEBUG=1 to enable debug output.
    """
    from .tool_registry import load_groups
    toolset_manager = mcp_server.manager
    # Load all tool definitions into manager
    load_groups(mcp_server)

    if toolsets is None:
        enabled = [DEFAULT_TOOL_GROUP]
    elif isinstance(toolsets, str):
        enabled = [g.strip() for g in toolsets.split(",") if g.strip()] or [DEFAULT_TOOL_GROUP]
    elif isinstance(toolsets, list):
        enabled = list(toolsets) or [DEFAULT_TOOL_GROUP]
    else:
        raise ValueError('toolset parameter should be string, e.g. [rds,rds_mssql_custom]')

    available_toolset_groups = toolset_manager.registered_tool_groups()
    invalid_toolset_groups = [g for g in enabled if g not in available_toolset_groups]
    if invalid_toolset_groups:
        raise ValueError(
            f"Unknown toolset group(s): [{','.join(sorted(invalid_toolset_groups))}] "
            f"Available groups: [{','.join(sorted(available_toolset_groups))}]"
        )

    toolset_manager.enable(*enabled)
    toolset_manager.register_enabled(mcp_server)

    # Debug output controlled by environment variable
    if os.getenv('TOOLSET_DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
        print("All registered groups:", toolset_manager.registered_tool_groups())
        print("Enabled groups:", toolset_manager.enabled_tool_groups())
        print("Actually registered tools:")
        for group, tools in toolset_manager.enabled_tools().items():
            print(f"  - group: {group}")
            for t in tools:
                print(f"    • {t.__name__}")
