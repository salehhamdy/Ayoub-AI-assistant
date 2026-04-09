"""
ayoub/modules/main_agent.py — Full ReAct agent with all tools.

CLI: ayoub -m "question"   (default mode)
     ayoub "question"       (bare string also routes here)

Loads all available tools and runs the ReAct loop.
"""
import asyncio

from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import ReActPrompt
from ayoub.agent.react_runtime import ReActRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.memory.file_memory import read_memory
from ayoub.tools.search_tool import AyoubSearchTool
from ayoub.tools.python_exec_tool import AyoubPythonExecTool
from ayoub.tools.scrape_tool import AyoubScrapeTool
from ayoub.tools.pdf_tool import AyoubPDFTool
from ayoub.tools.image_gen_tool import AyoubTxt2ImgTool, AyoubSketch2ImgTool
from ayoub.tools.system_tools import get_current_time, get_system_info
from ayoub.agent.toolkit import BaseTool
from ayoub.logger import get_logger

logger = get_logger("main-agent")

_EXAMPLE_WORKFLOW = """\
Example:
Thought: I need to search for recent AI news.
Action: search_tool
Action Input: latest AI research 2024

Observation: [search results ...]

Thought: I have enough information to summarise.
Action: finish
Final Answer: Here are the top AI stories ..."""


# Thin wrappers for system tools to fit BaseTool interface
class _TimeTool(BaseTool):
    def __init__(self):
        super().__init__("Get the current date and time", "get_current_time_tool")
    def execute_func(self, *_) -> str:
        return get_current_time()


class _SysTool(BaseTool):
    def __init__(self):
        super().__init__("Get information about the current operating system and Python version", "get_system_info_tool")
    def execute_func(self, *_) -> str:
        return str(get_system_info())


def _build_toolkit() -> ToolKit:
    return ToolKit(tools=[
        AyoubSearchTool(),
        AyoubPythonExecTool(),
        AyoubScrapeTool(),
        AyoubPDFTool(),
        AyoubTxt2ImgTool(),
        AyoubSketch2ImgTool(),
        _TimeTool(),
        _SysTool(),
    ])


def run_main(question: str, memory_name: str = "main_memory",
             max_steps: int = 10) -> str:
    """Full ReAct agent with all tools and optional memory context."""
    logger.info("MainAgent invoked | question=%r", question[:80])

    history = read_memory(memory_name)
    prompt  = ReActPrompt(
        question=question,
        example_workflow=_EXAMPLE_WORKFLOW,
        history=history,
    )
    llm     = AgentLLM()
    kit     = _build_toolkit()
    runtime = ReActRuntime(llm=llm, prompt=prompt, toolkit=kit)

    answer  = runtime.loop(agent_max_steps=max_steps, verbose_tools=True)
    logger.info("MainAgent completed.")
    return answer
