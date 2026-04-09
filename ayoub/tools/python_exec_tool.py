"""
ayoub/tools/python_exec_tool.py — Python code execution tool.

Cross-platform: uses sys.executable — never python3 or bash.
Extracts code from markdown fenced blocks if present.
"""
import re
import sys
import subprocess

from ayoub.agent.toolkit import BaseTool


class AyoubPythonExecTool(BaseTool):
    """Executes Python code and returns stdout + stderr."""

    def __init__(
        self,
        description: str = "Execute Python code and return the output. Wrap code in ```python ... ``` blocks.",
        tool_name: str = "python_tool",
        timeout: int = 30,
    ):
        super().__init__(description, tool_name)
        self.timeout = timeout

    def execute_func(self, code_input: str) -> str:
        code = self._extract_code(code_input.strip())
        if not code:
            return "[python_tool] No executable code provided."
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            output = result.stdout.strip()
            if result.stderr.strip():
                output += f"\n[stderr]:\n{result.stderr.strip()}"
            return output or "[python_tool] Code ran but produced no output."
        except subprocess.TimeoutExpired:
            return f"[python_tool] Timeout: code exceeded {self.timeout}s."
        except Exception as exc:
            return f"[python_tool] Execution error: {exc}"

    @staticmethod
    def _extract_code(text: str) -> str:
        """Strip markdown code fences if present, else return raw text."""
        match = re.search(r"```(?:python)?\s*\n?(.*?)```", text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else text
