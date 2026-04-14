# Changelog

## v2.0.0 — 2026-04-14

### Added
- Gemini 3 Flash Preview as default LLM
- Gemini Embedding 1 (gemini-embedding-001) with GeminiEmbedder class
- Gemma 3 family models (27B, 12B, 4B) via Gemini API
- Pollinations.ai for reliable image generation (6 FLUX models)
- Groq Llama 4 vision cascade for screen analysis
- ddgs package for real DuckDuckGo search results
- 5-mode screen analysis (describe/code/error/summarise/translate)

### Fixed
- Windows CP1252 encoding crashes in CLI output
- Vision fallback when Gemini free quota exhausted
- Image gen reliability (Gradio spaces often go offline)
- Search returning no results (ddgs replaces duckduckgo_search)

### Changed
- API_CALL_DELAY restored to 5 seconds for free tier safety
- Model switcher uses ASCII characters for Windows compatibility
