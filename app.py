# app.py — UI/UX upgraded (Full Gradient + Neon)
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import os
import io
import google.generativeai as genai
from pydub import AudioSegment
import speech_recognition as sr
from moviepy.editor import VideoFileClip

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="Audio/Video → Notes + Quiz",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Model name you already validated from list_models()
MODEL_NAME = "models/gemini-2.5-flash"  # fast + supports text generation
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------------------
# CSS (Full Gradient + Glass + Neon)
# ---------------------------
CSS = """
<style>
/* Animated gradient background */
.stApp {
  background: linear-gradient(120deg, #0f1020, #17182c, #121826);
  background-size: 400% 400%;
  animation: gradientMove 18s ease infinite;
}
@keyframes gradientMove {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

/* Global typography */
html, body, [class*="css"]  {
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji', 'Segoe UI Symbol';
}

/* App title gradient text */
.gradient-title {
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: 0.3px;
  background: linear-gradient(90deg, #8b5cf6, #22d3ee, #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 10px rgba(139,92,246,0.25));
}

/* Glass card containers */
.glass {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.35), inset 0 0 0 1px rgba(255,255,255,0.03);
  backdrop-filter: blur(12px);
  border-radius: 18px;
  padding: 1.1rem 1.2rem;
}

/* Subhead */
.subhead {
  color: #d1d5db;
  font-size: 0.98rem;
  margin-top: -6px;
}

/* Neon primary buttons */
.stButton > button {
  border-radius: 12px !important;
  padding: 0.7rem 1.1rem !important;
  font-weight: 700 !important;
  letter-spacing: .3px !important;
  border: 1px solid rgba(34,211,238,.45) !important;
  background: radial-gradient(120% 120% at 50% 120%, rgba(34,211,238,.25) 0%, rgba(34,211,238,.08) 45%, rgba(34,211,238,.02) 100%);
  color: #e6fbff !important;
  box-shadow: 0 0 20px rgba(34,211,238,.22), inset 0 0 8px rgba(34,211,238,.18);
  transition: transform .08s ease, box-shadow .15s ease, border-color .15s ease;
}
.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 28px rgba(34,211,238,.35), inset 0 0 10px rgba(34,211,238,.22);
  border-color: rgba(34,211,238,.8) !important;
}

/* Secondary pills */
.pill {
  display: inline-block;
  padding: .35rem .6rem;
  border-radius: 999px;
  font-size: .78rem;
  border: 1px solid rgba(148,163,184,.35);
  color: #cbd5e1;
  background: rgba(30,41,59,.45);
}

/* Expander styling */
.streamlit-expanderHeader {
  font-weight: 700 !important;
  letter-spacing: .3px;
}
.streamlit-expanderHeader:hover {
  filter: drop-shadow(0 0 8px rgba(34,211,238,.25));
}

/* Markdown output card style */
.output-card {
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148,163,184,.25);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  color: #e5e7eb;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(15,16,32,.95), rgba(17,24,39,.95));
  border-right: 1px solid rgba(148,163,184,.12);
}
.sidebar-title {
  font-weight: 800;
  font-size: 1.2rem;
  background: linear-gradient(90deg, #22d3ee, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.sidebar-small {
  color: #a3a3a3; font-size: .86rem;
}
.footer {
  opacity: .75; font-size: .82rem; color: #9ca3af; text-align:center; padding-top: .7rem;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------
# Helpers (same logic)
# ---------------------------
def video_to_audio(video_path: str) -> str:
    audio_path = "temp_audio.wav"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
    clip.close()
    return audio_path

def audio_to_text(audio_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)

def generate_notes(text: str) -> str:
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
You are a world-class note-maker. Summarize the following content in clean bullet points.
Keep it concise, logically grouped, and practical. Focus on key facts, definitions, steps, and outcomes.

Text:
{text}
"""
    resp = model.generate_content(prompt)
    return resp.text if hasattr(resp, "text") else str(resp)

def generate_quiz(text: str) -> str:
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
Create a 5-question quiz from this content. Mix formats:
- 3 multiple-choice (4 options each, mark the correct one)
- 1 short-answer
- 1 true/false
Keep questions unambiguous and practical.

Content:
{text}
"""
    resp = model.generate_content(prompt)
    return resp.text if hasattr(resp, "text") else str(resp)

def _bytes_from_str(s: str) -> bytes:
    return s.encode("utf-8") if s else b""

# ---------------------------
# SIDEBAR (Navigation/Meta)
# ---------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎧 Notes + Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-small">Audio/Video → Speech-to-Text → Notes & Quiz</div>', unsafe_allow_html=True)
    st.markdown("---")
    key_ok = bool(os.getenv("GOOGLE_API_KEY"))
    st.markdown(f"**Gemini Model**: <span class='pill'>{MODEL_NAME}</span>", unsafe_allow_html=True)
    st.markdown(f"**API Key**: <span class='pill' style='color:{'#22c55e' if key_ok else '#ef4444'}'>{'Loaded' if key_ok else 'Missing'}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Tip: Larger videos take longer. Prefer shorter clips for quick tests.")

# ---------------------------
# HEADER
# ---------------------------
st.markdown(
    """
    <div class="glass">
      <div class="gradient-title">🎙️ Audio / 🎥 Video → Notes + Quiz</div>
      <div class="subhead">Upload a file, we auto-transcribe it, then generate clean notes and a ready-to-use quiz.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ---------------------------
# MAIN LAYOUT
# ---------------------------
col_left, col_right = st.columns([1.15, 1])

with col_left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("#### Upload")
    uploaded = st.file_uploader(
        "Supported formats: MP3, WAV, MP4, MKV, MOV",
        type=["mp3", "wav", "mp4", "mkv", "mov"],
        help="For videos we’ll first extract audio automatically."
    )
    run_btn = st.button("⚡ Generate Notes & Quiz", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("#### Status")
    st.markdown(
        """
        <div class="output-card">
          <b>Pipeline</b><br>
          1) File → (Video→Audio if needed)<br>
          2) Speech-to-Text<br>
          3) Gemini Notes & Quiz
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# PROCESSING
# ---------------------------
if run_btn:
    if not uploaded:
        st.warning("Upload a file first.")
    else:
        try:
            # Save temp file
            ext = uploaded.name.split(".")[-1].lower()
            temp_path = f"uploaded_temp.{ext}"
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())

            # Video → Audio (if needed)
            if ext in ("mp4", "mkv", "mov"):
                with st.spinner("🎬 Extracting audio from video..."):
                    audio_path = video_to_audio(temp_path)
            else:
                audio_path = temp_path

            # Audio → Text
            with st.spinner("🎧 Converting audio to text..."):
                text_data = audio_to_text(audio_path)

            # Notes
            with st.spinner("📝 Generating Notes..."):
                notes = generate_notes(text_data)

            # Quiz
            with st.spinner("🧠 Generating Quiz..."):
                quiz = generate_quiz(text_data)

            # ---------------------------
            # OUTPUT UI
            # ---------------------------
            st.markdown("")
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            with st.expander("✅ Generated Notes", expanded=True):
                st.markdown(f"<div class='output-card'>{notes}</div>", unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download Notes (.txt)",
                    data=_bytes_from_str(notes),
                    file_name="notes.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="glass">', unsafe_allow_html=True)
            with st.expander("✅ Generated Quiz", expanded=True):
                st.markdown(f"<div class='output-card'>{quiz}</div>", unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download Quiz (.txt)",
                    data=_bytes_from_str(quiz),
                    file_name="quiz.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown(
    "<div class='footer'>Built for fast prototyping • Gradient Neon UI • Streamlit</div>",
    unsafe_allow_html=True
)
