"""
ayoub/agent/base_prompt.py — BasePrompt and ReActPrompt.

Ported from customAgents/agent_prompt/ with Ayoub persona.
"""


class BasePrompt:
    """Holds the prompt string and an optional image for multimodal use."""

    def __init__(self, prompt_string: str = "", img=None):
        self.prompt = prompt_string
        self.img = img


class ReActPrompt(BasePrompt):
    """
    Builds the ReAct system prompt for Ayoub.
    Slots {tool_names}, {tools_and_role}, {history}, {question}
    are filled by ReActRuntime.loop() before each call.
    """

    REACT_TEMPLATE = """\
You are Ayoub, a friendly and helpful AI assistant.
You are knowledgeable in programming, data science, machine learning, science, and math.
Your name is Ayoub. Always refer to yourself as Ayoub.

Conversation Memory:
{history}

You have access to the following tools:
{tools_and_role}

IMPORTANT: Follow this format EXACTLY for every step:

Thought: [Your reasoning on whether to use a tool or answer directly]
Action: [One of: "finish" OR one of: {tool_names}]
Action Input: [Input for the chosen tool — plain text or Python code block]

When you have all the information:
Thought: I now have everything I need to answer.
Action: finish
Final Answer: [Your complete, friendly answer]

Rules:
- Never skip Thought and Action, even for simple questions.
- Observations come from the tools — do NOT fabricate them.
- If a tool fails, try again once; if it still fails, state that clearly.
- Keep gathering information until you are CERTAIN you have enough.

Example workflow:
{example_workflow}

Let's begin!

Question: {question}
"""

    def __init__(
        self,
        question: str,
        example_workflow: str = "",
        prompt_string: str = "",
        history: str = "",
    ):
        filled = self.REACT_TEMPLATE.format(
            history=history,
            tools_and_role="{tools_and_role}",   # filled by runtime
            tool_names="{tool_names}",             # filled by runtime
            example_workflow=example_workflow,
            question=question,
        )
        combined = prompt_string + filled
        super().__init__(prompt_string=combined)
