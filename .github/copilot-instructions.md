# Repo-specific guidance for AI coding agents

This file summarizes the essential patterns and workflows to be immediately productive in this repository.

1. Purpose & Big Picture
- This is a Streamlit-based comparison UI for RAG + LLM inference (see `app_compare.py` and `app_compare2.py`).
- Primary flow: receive user prompt → RAG retrieval from AWS Knowledge Base (Bedrock Agent) → call two LLMs in parallel → render a side-by-side comparison and log results to Google Sheets.

2. Key integration points
- AWS Bedrock: `get_aws_runtime()` and `get_aws_agent()` create Bedrock clients and are used for model invocation and retrieval (`invoke_model`, `retrieve`). See `app_compare.py: call_single_model()` and `retrieve_context()`.
- DeepSeek: `OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")` — invoked in `call_single_model` / `ask_ai`.
- Google GenAI (Gemini): configured via `genai.configure(api_key=GEMINI_API_KEY)` and used with `genai.GenerativeModel(...)`.
- Google Sheets: `credentials.json` + `ServiceAccountCredentials` + `gspread` used in `get_sheet_client()` and `save_to_sheet()` (see `app_compare2.py`).

3. Secrets & config conventions
- Prefer `st.secrets` (Streamlit secrets, e.g. `.streamlit/secrets.toml`) as in `app_compare.py`. `app_compare2.py` contains hard-coded API keys — treat these as sensitive and remove before committing.
- Required credentials: AWS keys, DEEPSEEK_API_KEY, GEMINI_API_KEY, and `credentials.json` (Google service account). The app will error/stop if secrets are missing.

4. Code patterns to follow / extend
- Models registry: add new models to the `MODELS` dict (example in both files). Keys: human-friendly name → object with `type`, `id`, and optional `icon`/`color`.
  - Example: `"Gemini 2.0 Flash": {"type":"gemini","id":"gemini-2.0-flash","icon":"✨"}`
- Unified caller: implementations centralize per-type logic in `call_single_model()` / `ask_ai()` — add provider-specific branches here rather than scattering invocation logic.
- Cost estimation: `calculate_cost(...)` uses a rough chars→tokens approximation and `MODEL_PRICING` mapping. Update `MODEL_PRICING` when adding models.
- Caching: use `@st.cache_resource` for heavy external clients (AWS/DeepSeek) and `@st.cache_data` for short-lived data (history). Keep TTLs small for dynamic data.
- Parallelism: the UI uses `concurrent.futures.ThreadPoolExecutor` to call two models concurrently. Preserve this pattern if adding multi-model comparisons.

5. Running & debugging (local dev)
- Install runtime deps (create virtualenv first):
  - `python -m venv .venv && source .venv/bin/activate.csh` (csh-compatible activate command)
  - `pip install streamlit boto3 google-auth-oauthlib gspread oauth2client openai google-generative-ai pandas` (adjust versions as needed)
- Run the app:
  - `streamlit run app_compare.py` (or `app_compare2.py` for the legacy/hardcoded variant)
- Secrets setup:
  - Preferred: create `.streamlit/secrets.toml` with the keys used in `app_compare.py`.
  - Ensure `credentials.json` (Google service account) is present for sheet writes.

6. Tests, logs, and observability
- No formal tests in repo. For interactive validation, run the app locally and test queries that should return KB results.
- Runtime errors from provider calls are caught and surfaced in the UI (look for `⚠️ Error:` strings or `Error:` messages in responses).

7. Common change patterns
- To add a new model/provider:
  1. Register entry in `MODELS`.
  2. Update `MODEL_PRICING` if you want cost estimates.
  3. Extend `call_single_model()` / `ask_ai()` with a new `m_type` branch that constructs provider-specific payloads.
  4. Update UI select lists (they read from `MODELS` dynamically).

8. Security notes (visible in code)
- `app_compare2.py` contains plaintext API keys. Do not leave these in git history. Replace with `st.secrets` or environment-backed secrets.
- `credentials.json` is required for Sheets and must be stored securely (not checked-in unless intentionally secret-managed).

If anything here is unclear or you want more detail on a specific part (e.g., exact Bedrock payloads, adding a new provider, or converting keys to `st.secrets`), tell me which section to expand. 
