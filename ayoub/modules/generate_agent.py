"""
ayoub/modules/generate_agent.py — Image generation agent.

CLI: ayoub -G "a futuristic city at sunset"
"""
from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import ReActPrompt
from ayoub.agent.react_runtime import ReActRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.tools.image_gen_tool import AyoubTxt2ImgTool, AyoubSketch2ImgTool
from ayoub.logger import get_logger

logger = get_logger("generate-agent")

_EXAMPLE_WORKFLOW = """\
Thought: The user wants an image generated from their prompt.
Action: image_to_text_tool
Action Input: {prompt}

Observation: Images saved to: output/imgs/...

Thought: The images have been generated and saved.
Action: finish
Final Answer: Your images have been generated and saved to output/imgs/."""


def run_generate(prompt: str) -> str:
    """Generate images from a text prompt."""
    logger.info("GenerateAgent invoked | prompt=%r", prompt[:80])

    react_prompt = ReActPrompt(
        question=f"Generate images for: {prompt}",
        example_workflow=_EXAMPLE_WORKFLOW.format(prompt=prompt),
    )
    llm     = AgentLLM()
    kit     = ToolKit(tools=[AyoubTxt2ImgTool(), AyoubSketch2ImgTool()])
    runtime = ReActRuntime(llm=llm, prompt=react_prompt, toolkit=kit)

    answer = runtime.loop(agent_max_steps=4, verbose_tools=True)
    logger.info("GenerateAgent completed.")
    return answer
