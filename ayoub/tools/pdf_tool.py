"""
ayoub/tools/pdf_tool.py — PDF reader tool.

Ported from hereiz. Uses PyPDF2; pathlib.Path for cross-platform paths.
"""
from pathlib import Path
import PyPDF2

from ayoub.agent.toolkit import BaseTool


class AyoubPDFTool(BaseTool):
    """Reads all text from a PDF file given its absolute or relative path."""

    def __init__(
        self,
        description: str = "Read and extract text from a PDF file. Provide the file path as input.",
        tool_name: str = "readpdf_tool",
    ):
        super().__init__(description, tool_name)

    def execute_func(self, pdf_path: str) -> str:
        path = Path(pdf_path.strip())
        if not path.exists():
            return f"[readpdf_tool] File not found: {path}"
        if path.suffix.lower() != ".pdf":
            return f"[readpdf_tool] Not a PDF file: {path}"
        try:
            reader = PyPDF2.PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
            return text if text else "[readpdf_tool] PDF has no extractable text."
        except Exception as exc:
            return f"[readpdf_tool] Error reading PDF: {exc}"
