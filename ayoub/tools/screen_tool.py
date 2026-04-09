"""
ayoub/tools/screen_tool.py — Screen capture tool (wraps ayoub.screen_capture).
"""
from ayoub.agent.toolkit import BaseTool
from ayoub.screen_capture import capture_screen
from ayoub.config import TMP_DIR


class AyoubScreenTool(BaseTool):
    """Takes a screenshot and returns the file path for vision analysis."""

    def __init__(
        self,
        description: str = "Take a screenshot of the current screen and return the image path",
        tool_name: str = "screen_tool",
    ):
        super().__init__(description, tool_name)
        TMP_DIR.mkdir(parents=True, exist_ok=True)

    def execute_func(self, *args) -> str:
        try:
            path = capture_screen(TMP_DIR)
            return str(path)
        except Exception as exc:
            return f"[screen_tool] Failed to capture screen: {exc}"
