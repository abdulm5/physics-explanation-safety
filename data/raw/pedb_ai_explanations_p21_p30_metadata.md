# PEDB AI Generation Metadata (P21-P30)

- Date: 2026-04-11
- Provider: OpenRouter
- Models:
  - `openai/gpt-5.3-chat` (mapped to ChatGPT / GPT latest lane)
  - `anthropic/claude-sonnet-4.6` (Sonnet lane)
- Prompt template:
  - "Explain this physics concept to a first-year college student in about 100 words. Be conceptually precise, pedagogically clear, and avoid unnecessary jargon. Include the relevant physical principle and one intuitive bridge/example if helpful. Return only one plain paragraph with no title and no bullet points. Question: <prompt>"
- Output file:
  - `data/raw/pedb_ai_explanations_p21_p30.csv`
- Rows generated:
  - 20 (10 prompts x 2 models)
