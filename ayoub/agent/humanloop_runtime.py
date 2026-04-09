"""
ayoub/agent/humanloop_runtime.py — HumanLoopRuntime.

Used by -aH mode: prompts the user for follow-up after each LLM response.
"""
from ayoub.agent.base_runtime import BaseRuntime


class HumanLoopRuntime(BaseRuntime):
    """
    Runs the LLM and, if activate_loop=True, asks the user whether to continue.
    The conversation continues until the user types 'done', 'exit', or presses Enter.
    """

    def loop(self, activate_loop: bool = True) -> str:  # type: ignore[override]
        response = self.step()

        if not activate_loop:
            return response

        while True:
            print()
            user_input = input("You (follow-up or 'done'): ").strip()
            if not user_input or user_input.lower() in ("done", "exit", "quit", "q"):
                break
            self.prompt.prompt += f"\nHuman: {user_input}\nAyoub:"
            response = self.step()

        return response
