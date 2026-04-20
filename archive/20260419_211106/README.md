# Karan AI Voice Agent

This project is a DM-to-audio app:
- User enters a DM-style question
- A Smallest Atoms agent generates the reply text
- SmallestAI converts that reply to speech
- Streamlit plays and downloads the audio

## Project Structure

```text
.
├── app.py
├── atoms.py
├── llm.py
├── tts.py
├── prompts.py
├── requirements.txt
├── .env.example
└── data/
    ├── about_me.md
    ├── learning_path.md
    └── personal_brand.md
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure env vars (copy `.env.example` to `.env` and fill values):

```bash
cp .env.example .env
```

Required:
- `SMALLEST_API_KEY`
- `SMALLEST_ATOMS_AGENT_ID`
- `SMALLEST_ATOM_VOICE_ID` or `SMALLEST_VOICE_ID`

Defaults already set for:
- `SMALLEST_BASE_URL=https://api.smallest.ai`
- `SMALLEST_ATOMS_BASE_URL=https://api.smallest.ai/atoms/v1`

3. Optional if your Atoms workspace uses a custom text route:

```bash
SMALLEST_ATOMS_MESSAGE_PATH=/agent/{agent_id}/message
```

4. Run Streamlit:

```bash
streamlit run app.py
```

## How It Works

1. User enters a question in the UI.
2. `atoms.py` sends the message to your configured Atoms agent.
3. `tts.py` sends the generated reply to SmallestAI.
4. Streamlit plays and downloads the audio.

## Notes

- `llm.py` and the markdown files can still help you prepare the Atoms persona and knowledge base, but the Streamlit runtime now expects an Atoms agent.
- Set a valid Atoms agent ID and voice ID in `.env` before running the app.
