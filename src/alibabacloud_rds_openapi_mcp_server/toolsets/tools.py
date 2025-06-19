# -*- coding: utf-8 -*-

from __future__ import annotations
from .toolsets import ToolsetManager, ToolsetMCP

from . import rds_custom

from typing import Callable, Any, Dict

__tools__: list[tuple[Callable, dict[str, Any]]] = []

def tool(**kwargs):
    def decorator(func):
        __tools__.append((func, kwargs))
        return func
    return decorator

def load_groups(manamanager: ToolsetManager, mcp: ToolsetMCP) -> None:
    """Assign selected tools to groups using ``ToolsetManager``."""
    for func, meta in rds_custom.__tools__:
        mcp.tool(**meta)(func)