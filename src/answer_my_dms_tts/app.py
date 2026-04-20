from __future__ import annotations

import json
import os
import re

import streamlit as st

from .config import load_settings
from .dm_agent import generate_dm_reply_sync
from .tts import TTSError, synthesize_speech

LANGUAGES: dict[str, dict[str, str]] = {
    "English": {"browser": "en-US", "tts": "en"},
    "Hindi": {"browser": "hi-IN", "tts": "hi"},
    "Marathi": {"browser": "mr-IN", "tts": "mr"},
    "Gujarati": {"browser": "gu-IN", "tts": "gu"},
    "Punjabi": {"browser": "pa-IN", "tts": "pa"},
    "Bengali": {"browser": "bn-IN", "tts": "bn"},
    "Tamil": {"browser": "ta-IN", "tts": "ta"},
    "Telugu": {"browser": "te-IN", "tts": "te"},
    "Kannada": {"browser": "kn-IN", "tts": "kn"},
    "Malayalam": {"browser": "ml-IN", "tts": "ml"},
    "Spanish": {"browser": "es-ES", "tts": "es"},
    "French": {"browser": "fr-FR", "tts": "fr"},
    "German": {"browser": "de-DE", "tts": "de"},
}


def render_speech_button(text: str, language_code: str) -> None:
    payload = json.dumps({"text": text, "lang": language_code})
    st.components.v1.html(
        f"""
        <div style="display:flex;gap:12px;align-items:center;">
          <button id="speak-btn" style="padding:10px 16px;border-radius:999px;border:1px solid #222;background:#111;color:#fff;cursor:pointer;">
            Speak Reply
          </button>
          <span style="font:14px sans-serif;color:#555;">Uses your browser voice for the selected language.</span>
        </div>
        <script>
          const payload = {payload};
          const button = document.getElementById("speak-btn");
          button.addEventListener("click", () => {{
            const synth = window.speechSynthesis;
            if (!synth) {{
              alert("Speech synthesis is not available in this browser.");
              return;
            }}
            synth.cancel();
            const utterance = new SpeechSynthesisUtterance(payload.text);
            utterance.lang = payload.lang;
            synth.speak(utterance);
          }});
        </script>
        """,
        height=72,
    )


def clean_tts_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"[*_`#>-]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace(" - ", ", ")
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def render_app() -> None:
    st.set_page_config(page_title="DM Reply Agent", page_icon="💬", layout="wide")

    st.title("DM Reply Agent")
    st.caption("Type a DM, choose a language, and generate audio.")

    with st.sidebar:
        st.subheader("Model")
        settings = load_settings()
        st.code(settings.llm_model, language=None)
        st.caption("Provider is configured through `.env` and currently targets an OpenAI-compatible endpoint.")
        voice_id = os.getenv("SMALLEST_ATOM_VOICE_ID", "").strip() or os.getenv("SMALLEST_VOICE_ID", "").strip()
        if voice_id and os.getenv("SMALLEST_API_KEY", "").strip():
            st.caption("Audio output is enabled with Smallest TTS.")
        else:
            st.caption("Audio output is not configured. Browser speech fallback will be used.")

    left, right = st.columns([1.3, 0.9], gap="large")

    with left:
        question = st.text_area("Type your question", height=220, placeholder="Paste the incoming DM or describe what you want to reply.")
        language = st.selectbox("Reply language", list(LANGUAGES.keys()), index=0)
        generate = st.button("Generate Audio", use_container_width=True, type="primary")

    with right:
        st.subheader("To Try This")
        st.markdown(
            """
            Built with [Smallest.ai](https://smallest.ai), focused on fast voice and agent experiences.

            Explore Atoms Agent docs here:
            [atoms-docs.smallest.ai/dev/introduction/overview](https://atoms-docs.smallest.ai/dev/introduction/overview)
            """
        )

    if generate:
        if not question.strip():
            st.warning("Enter a DM or prompt first.")
        else:
            with st.spinner("Generating reply..."):
                reply = generate_dm_reply_sync(
                    settings=settings,
                    question=question,
                    language_label=language,
                    tone="Friendly",
                )
            st.session_state["reply"] = reply
            st.session_state["reply_language_code"] = LANGUAGES[language]["browser"]
            st.session_state["reply_audio"] = None

            if voice_id and os.getenv("SMALLEST_API_KEY", "").strip():
                try:
                    audio = synthesize_speech(
                        text=clean_tts_text(reply),
                        language_code=LANGUAGES[language]["tts"],
                        voice_id=voice_id,
                        speed=0.85,
                    )
                    st.session_state["reply_audio"] = audio
                    st.audio(audio, format="audio/mp3")
                    st.download_button(
                        "Download MP3",
                        data=audio,
                        file_name="dm-reply.mp3",
                        mime="audio/mpeg",
                        use_container_width=True,
                    )
                except TTSError as err:
                    st.warning(f"Audio generation failed: {err}")
                    render_speech_button(reply, LANGUAGES[language]["browser"])
            else:
                render_speech_button(reply, LANGUAGES[language]["browser"])
    elif "reply" in st.session_state:
        if st.session_state.get("reply_audio"):
            st.audio(st.session_state["reply_audio"], format="audio/mp3")
            st.download_button(
                "Download MP3",
                data=st.session_state["reply_audio"],
                file_name="dm-reply.mp3",
                mime="audio/mpeg",
                use_container_width=True,
            )
        else:
            render_speech_button(st.session_state["reply"], st.session_state["reply_language_code"])


if __name__ == "__main__":
    render_app()
