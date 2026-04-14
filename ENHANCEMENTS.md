# Search & Vision Enhancement Notes

## Search Tool (ddgs)
- Upgraded from duckduckgo_search to ddgs (official rename)
- Now returns real URLs (no redirect wrappers)
- Query cleaning strips LLM inline notes before searching

## Image Generation (Pollinations.ai)
- Primary: https://image.pollinations.ai — free, no API key
- 6 FLUX models with auto-detection from prompt keywords:
  - lux (default), lux-realism, lux-anime, lux-3d, lux-cablyai, 	urbo
- Prompt auto-enhancement with model-specific quality keywords
- Fallback: Gradio spaces (mukaist, sdxl-turbo)

## Screen Analysis Vision Cascade
- Provider 1: Google Gemini 2.0 Flash (primary)
- Provider 2: Groq Llama 4 Scout 17B (auto-fallback on 429)
- Provider 3: Groq Llama 4 Maverick (secondary fallback)

## Screen Analysis Modes (auto-detected)
| Keyword | Mode | Description |
|---|---|---|
| code, script, function | CODE | Code review + bug detection |
| error, crash, exception | ERROR | Root cause + fix |
| summarise, summary | SUMMARISE | Key points |
| translate, arabic | TRANSLATE | Full translation |
| read, extract, text | OCR | Full text extraction |
| (anything else) | DESCRIBE | Visual description |
