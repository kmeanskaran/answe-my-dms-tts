from __future__ import annotations

import logging
import os
import re

import streamlit as st
from dotenv import load_dotenv

from atoms import AtomsError, generate_dm_reply
from tts import TTSError, synthesize_speech

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
st.set_page_config(page_title="Karan Voice Agent", page_icon="🎙️")

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Tamil": "ta",
    "Telugu": "te",
    "Japanese": "ja",
}


def clean_tts_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"[*_`#>-]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace(" - ", ", ")
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


st.title("Karan AI Voice Agent")
st.caption("Ask a DM-style question and generate an audio reply.")

question = st.text_area("Question", height=140)
language = st.selectbox("Language", list(LANGUAGES))

voice_id = os.getenv("SMALLEST_ATOM_VOICE_ID", "").strip() or os.getenv("SMALLEST_VOICE_ID", "").strip()
atoms_agent_id = os.getenv("SMALLEST_ATOMS_AGENT_ID", "").strip()

if st.button("Generate Audio", use_container_width=True):
    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    if not atoms_agent_id:
        st.error("Set SMALLEST_ATOMS_AGENT_ID in your environment to use the Atoms DM agent.")
        st.stop()

    if not voice_id:
        st.error("Set SMALLEST_ATOM_VOICE_ID or SMALLEST_VOICE_ID in your environment.")
        st.stop()

    try:
        answer = generate_dm_reply(
            agent_id=atoms_agent_id,
            question=question,
            language_label=language,
        )
        spoken_answer = clean_tts_text(answer)
        audio = synthesize_speech(
            text=spoken_answer,
            language_code=LANGUAGES[language],
            voice_id=voice_id,
            speed=0.85,
        )
    except AtomsError as err:
        st.error(str(err))
        st.stop()
    except TTSError as err:
        st.error(str(err))
        logger.exception("TTS generation failed")
        st.stop()

    st.audio(audio, format="audio/mp3")
    st.download_button(
        "Download MP3",
        data=audio,
        file_name="karan-voice-agent-response.mp3",
        mime="audio/mpeg",
        use_container_width=True,
    )

st.divider()
st.caption(
    "Flow: DM question -> Atoms agent reply -> Smallest TTS audio. "
    "Set `SMALLEST_ATOMS_MESSAGE_PATH` only if your Atoms workspace uses a custom message route."
)
