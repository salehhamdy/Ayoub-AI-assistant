"""
ayoub/agent/base_runtime.py — BaseRuntime.

Ported from customAgents/runtime/base_runtime.py
"""
from ayoub.agent.toolkit import ToolKit
from ayoub.agent.base_prompt import BasePrompt


class BaseRuntime:
    """
    Drives a single LLM + prompt + toolkit combination.
    Subclasses override step() and loop() for specialised behaviour.
    """

    def __init__(self, llm, prompt: BasePrompt, toolkit: ToolKit):
        self.llm = llm
        self.prompt = prompt
        self.toolkit = toolkit if toolkit is not None else ToolKit()

    # ── Core step ─────────────────────────────────────────────────────────────

    def step(self) -> str:
        """Run one LLM call, stream output to the terminal, return full text."""
        response = ""
        for chunk in self.llm.stream(self.prompt.prompt):
            print(chunk, end="", flush=True)
            response += chunk
        print()  # newline after streaming
        return response

    def loop(self, n_steps: int = 1) -> str:
        """Run n_steps sequential LLM calls, appending each response to the prompt."""
        response = ""
        for _ in range(n_steps):
            response = self.step()
            self.prompt.prompt += f"\n{response}"
        return response

    # ── Utilities ─────────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.prompt.prompt = ""
        self.prompt.img = None

    def update_prompt(self, new_prompt: str) -> None:
        self.prompt.prompt = new_prompt

    def add_to_prompt(self, text: str) -> None:
        self.prompt.prompt += text

    def get_toolkit_info(self) -> dict:
        return {
            "available_tools": self.toolkit.list_tools(),
            "tool_count": len(self.toolkit),
        }

    def __str__(self) -> str:
        return (
            f"BaseRuntime(llm={type(self.llm).__name__}, "
            f"prompt_len={len(self.prompt.prompt)}, "
            f"tools={self.toolkit.list_tools()})"
        )
