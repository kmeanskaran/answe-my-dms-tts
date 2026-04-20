# DM Reply Agent

DM-focused reply generator with Streamlit UI, Atoms agent runtime, optional knowledge-base context, and optional Smallest TTS audio output.

## Project Structure

```text
.
├── app.py                         # Streamlit launcher (root entrypoint)
├── main.py                        # Atoms runtime launcher (root entrypoint)
├── src/
│   └── answer_my_dms_tts/
│       ├── app.py                 # Streamlit app logic
│       ├── main.py                # Atoms app runtime
│       ├── config.py
│       ├── dm_agent.py
│       ├── kb_manager.py
│       ├── prompts.py
│       └── tts.py
├── knowledge/
│   └── dm_kb.md                   # Optional local KB context file
├── archive/
│   └── 20260419_211106/           # Legacy snapshot (code/docs only)
└── data/                          # Local-use data (kept outside archive + gitignored)
```

`data/` is intentionally outside `archive/` and excluded from Git tracking.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment placeholders:

```bash
cp .env.example .env
```

3. Run Streamlit app:

```bash
streamlit run app.py
```

4. Optional Atoms runtime:

```bash
python main.py
```

## Notes

- `.env` and `.env.example` are kept with empty placeholders only.
- Secrets and local data should never be committed.
- Legacy code history remains in `archive/`.
