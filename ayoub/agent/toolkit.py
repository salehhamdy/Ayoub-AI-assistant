"""
ayoub/agent/toolkit.py — BaseTool and ToolKit classes.

Ported and renamed from hereiz-AI-terminal-assistant/customAgents/agent_tools/base_tools.py
"""
from typing import Any, Dict, List, Optional


class BaseTool:
    """Base class for individual agent tools."""

    def __init__(self, description: str, tool_name: str = None):
        self.description = description
        self.tool_name = self.__class__.__name__ if tool_name is None else tool_name

    def execute_func(self, *params: Any) -> Any:
        """Execute the tool. Must be overridden by subclasses."""
        raise NotImplementedError(
            f"Tool '{self.tool_name}' must implement execute_func(). Params: {params}"
        )

    def get_tool_info(self) -> str:
        return f"Tool Name: {self.tool_name}, Description: {self.description}"


class ToolKit:
    """Container that manages a collection of BaseTool instances."""

    def __init__(self, tools: List[BaseTool] = None):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_names: List[str] = []
        self.tool_descriptions: Dict[str, str] = {}

        if tools:
            for tool in tools:
                self._register(tool)

        self.tool_instructions = self._format_instructions()

    # ── Registration ──────────────────────────────────────────────────────────

    def _register(self, tool: BaseTool) -> None:
        self.tools[tool.tool_name] = tool
        self.tool_names.append(tool.tool_name)
        self.tool_descriptions[tool.tool_name] = tool.description
        self.tool_instructions = self._format_instructions()

    def add_tool(self, tool: BaseTool) -> None:
        self._register(tool)

    def remove_tool(self, tool_name: str) -> None:
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.tool_names.remove(tool_name)
            del self.tool_descriptions[tool_name]
            self.tool_instructions = self._format_instructions()
        else:
            raise ValueError(f"Tool '{tool_name}' not found in ToolKit.")

    # ── Execution ─────────────────────────────────────────────────────────────

    def execute_tool(self, tool_name: str, *params: Any) -> Any:
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in ToolKit.")
        return self.tools[tool_name].execute_func(*params)

    # ── Inspection ────────────────────────────────────────────────────────────

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        return list(self.tool_names)

    def _format_instructions(self) -> str:
        return "\n".join(
            f"({name}): {desc}" for name, desc in self.tool_descriptions.items()
        )

    def clear_tools(self) -> None:
        self.tools.clear()
        self.tool_names.clear()
        self.tool_descriptions.clear()
        self.tool_instructions = ""

    def __len__(self) -> int:
        return len(self.tools)

    def __repr__(self) -> str:
        return f"ToolKit(tools={self.tool_names})"
