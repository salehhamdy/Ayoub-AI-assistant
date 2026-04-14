# Gemini Model Reference

## Available Generation Models (via Gemini API free tier)

| Model | RPM | Notes |
|---|---|---|
| gemini-3-flash-preview | High | Latest Gemini 3, preview tier |
| gemini-2.5-flash | 15 | Stable |
| gemini-2.5-pro | 5 | Most capable |
| gemini-2.0-flash | 15 | Stable |
| gemini-2.0-flash-lite | 30 | Lightweight |
| gemma-3-27b-it | 30 | Gemma open-weight |
| gemma-3-12b-it | 30 | Gemma open-weight |
| gemma-3-4b-it | 30 | Gemma open-weight, fastest |

## Embedding Model

| Model | RPM | Dimensions |
|---|---|---|
| gemini-embedding-001 | 100 | 3072 |

## Vision Models (auto-cascade)
1. gemini-2.0-flash (primary, Gemini vision)
2. meta-llama/llama-4-scout-17b-16e-instruct (Groq fallback)
3. meta-llama/llama-4-maverick-17b-128e-instruct (Groq fallback 2)
