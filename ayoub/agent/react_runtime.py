"""
ayoub/agent/react_runtime.py — ReActRuntime.

Ported and refactored from customAgents/runtime/react_runtime.py.
Drives the Thought → Action → Observation → Final Answer loop.
"""
import warnings
from typing import Dict, Optional
from colorama import Fore, Style

from ayoub.agent.base_runtime import BaseRuntime
from ayoub.agent.base_prompt import BasePrompt
from ayoub.agent.toolkit import ToolKit


class ReActRuntime(BaseRuntime):

    def __init__(self, llm, prompt: BasePrompt, toolkit: ToolKit):
        super().__init__(llm, prompt, toolkit)

    # ── Step ──────────────────────────────────────────────────────────────────

    def step(self) -> Dict[str, str]:
        """Run one LLM call, print streamed output, parse and return the response dict."""
        response = ""
        for chunk in self.llm.stream(self.prompt.prompt):
            print(Fore.LIGHTGREEN_EX + chunk + Style.RESET_ALL, end="", flush=True)
            response += chunk
        print()
        return self._parse_response(response)

    # ── Loop ──────────────────────────────────────────────────────────────────

    def loop(self, agent_max_steps: int = 10, verbose_tools: bool = False) -> str:
        """
        ReAct loop: Thought → Action → Observation → repeat until 'finish'.
        Returns the Final Answer string.
        """
        # Inject tool info into the prompt
        if len(self.toolkit) > 0:
            self.prompt.prompt = self.prompt.prompt.replace(
                "{tool_names}", " ".join(self.toolkit.tool_names)
            ).replace("{tools_and_role}", self.toolkit.tool_instructions)
        else:
            self.prompt.prompt = self.prompt.prompt.replace(
                "{tool_names}", "**No tools — use own knowledge only**"
            ).replace(
                "{tools_and_role}",
                "(no tools available, only the 'finish' action is allowed)",
            )

        for iteration in range(agent_max_steps):
            print(f"\n{Fore.LIGHTCYAN_EX}[Ayoub — step {iteration + 1}]{Style.RESET_ALL}")
            parsed = self.step()

            if not parsed:
                continue

            action = parsed.get("Action", "").strip()

            # ── Finish ────────────────────────────────────────────────────────
            if action.lower() == "finish":
                final = parsed.get("Final Answer", "").strip()
                print(f"\n{Fore.LIGHTYELLOW_EX}[Final Answer]{Style.RESET_ALL}")
                return final

            # ── Tool call ─────────────────────────────────────────────────────
            if len(self.toolkit) > 0:
                if action not in self.toolkit.tool_names:
                    warnings.warn(f"Unknown action: '{action}'. Skipping iteration.")
                    continue

                action_input = parsed.get("Action Input", "").strip()

                try:
                    tool_result = self.toolkit.execute_tool(action, action_input)
                except Exception as exc:
                    tool_result = f"[Tool error: {exc}]"
                    warnings.warn(str(exc))

                if verbose_tools:
                    print(
                        f"\n{Fore.LIGHTYELLOW_EX}[Tool: {action}]{Style.RESET_ALL}\n"
                        f"{tool_result}\n"
                    )

                self.prompt.prompt += (
                    f"\nThought: {parsed.get('Thought', '')}"
                    f"\nAction: {action}"
                    f"\nAction Input: {action_input}"
                    f"\nObservation: {tool_result}"
                )

        return "Maximum iterations reached without a final answer."

    # ── Parser ────────────────────────────────────────────────────────────────

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse LLM output into a dict with Thought / Action / Action Input / Final Answer."""
        parsed: Dict[str, str] = {}
        current_key: Optional[str] = None
        multiline = False

        for line in response.split("\n"):
            if ":" in line and not multiline:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()

                if key in ("Thought", "Action", "Action Input", "Observation", "Final Answer"):
                    current_key = key
                    if key == "Action Input":
                        multiline = True
                        parsed[current_key] = value
                    elif key == "Final Answer":
                        # Capture everything after "Final Answer:" as the answer
                        parsed[current_key] = response.split("Final Answer:", 1)[1].strip()
                        return parsed
                    else:
                        parsed[current_key] = value

            elif multiline and current_key == "Action Input":
                parsed[current_key] = parsed.get(current_key, "") + "\n" + line
                if line.strip().endswith("```"):
                    multiline = False

            elif current_key:
                parsed[current_key] = parsed.get(current_key, "") + " " + line.strip()

        return parsed
