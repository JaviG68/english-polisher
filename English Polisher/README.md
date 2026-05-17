# English Polisher

A small web app that analyzes, corrects and improves English text and explains corrections in Spanish.

The app follows this workflow for each input text:

1. Read the input text.
2. Detect grammatical mistakes and stylistic issues.
3. Produce a corrected, more natural/colloquial version.
4. Provide Spanish explanations for each correction.

This repository contains a conservative, rule-based implementation intended as a local, offline prototype. For production-level quality, integrate an LLM (instructions in the next section).

## Quick start (macOS / bash)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Run the Flask app
python app.py
# Open http://127.0.0.1:5000 in your browser
```

## Files of interest

- `app.py` — Flask web server and API endpoint `/api/polish`
- `polisher.py` — Core rule-based polishing engine (returns corrections and Spanish explanations)
- `templates/index.html` — Minimal web UI to try the app
- `tests/test_polisher.py` — Basic unit tests for the polisher

## Integrating an LLM

The current implementation is rule-based and conservative. To use an LLM for higher-quality corrections:

- Add an API client (OpenAI, Anthropic, etc.) in `polisher.py` or a separate module
- Keep the output shape: `{original, improved, corrections: [{orig, suggestion, explanation_es, type}]}`
- Store API keys in environment variables and never commit them

## Feedback

Tell me if you prefer a different tone, more aggressive rewriting, or direct integration with OpenAI/Anthropic and I will update the code.
