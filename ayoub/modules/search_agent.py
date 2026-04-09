"""
ayoub/modules/search_agent.py — Focused web search agent.

CLI: ayoub -s "query"
     ayoub -fs "query"   (full search — scrapes multiple links)
"""
from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import ReActPrompt
from ayoub.agent.react_runtime import ReActRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.tools.search_tool import AyoubSearchTool
from ayoub.tools.scrape_tool import AyoubScrapeTool
from ayoub.tools.python_exec_tool import AyoubPythonExecTool
from ayoub.logger import get_logger

logger = get_logger("search-agent")

_EXAMPLE_WORKFLOW = """\
Thought: I need to search the internet for this topic.
Action: search_tool
Action Input: {query}

Observation: [search results ...]

Thought: I have enough information to answer.
Action: finish
Final Answer: Based on my research ..."""


def run_search(query: str, full: bool = False) -> str:
    """
    Run a web search and return a summary.
    full=True enables scraping of multiple URLs.
    """
    logger.info("SearchAgent invoked | full=%s | query=%r", full, query[:80])

    tools = [AyoubSearchTool(num_top_results=3 if full else 1), AyoubPythonExecTool()]
    if full:
        tools.insert(1, AyoubScrapeTool())

    prompt = ReActPrompt(
        question=query,
        example_workflow=_EXAMPLE_WORKFLOW.format(query=query),
    )
    llm     = AgentLLM()
    kit     = ToolKit(tools=tools)
    runtime = ReActRuntime(llm=llm, prompt=prompt, toolkit=kit)

    answer = runtime.loop(agent_max_steps=6, verbose_tools=True)
    logger.info("SearchAgent completed.")
    return answer
