# ✅ FINAL PREMIUM VERSION — Dark UI + Big Notes + Bullet Points
# ✅ Fixed Download + Proper Educational Notes (NOT video description)
# ✅ Fully polished for college-level project

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import subprocess
import google.generativeai as genai
import speech_recognition as sr


# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="AI Notes & Quiz Generator",
    page_icon="🎧",
    layout="wide",
)

MODEL_NAME = "models/gemini-2.5-flash"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# -----------------------------------------------------
# ✅ DARK PREMIUM UI
# -----------------------------------------------------
CSS = """
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* DARK BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0b0d16, #0d1119, #090a10);
    color: #e5e7eb;
}

/* HERO BANNER */
.hero {
    background: url('https://images.unsplash.com/photo-1535223289827-42f1e9919769?q=80&w=1600')
        center/cover no-repeat;
    padding: 2.7rem;
    border-radius: 20px;
    box-shadow: 0px 6px 30px rgba(0,0,0,0.45);
    position: relative;
}
.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.55);
    border-radius: 20px;
}
.hero h1, .hero p {
    position: relative;
    z-index: 2;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    color: #f9fafb;
}
.hero p {
    color: #d1d5db;
    font-size: 1.15rem;
}

/* GLASS CARD */
.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 1.6rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    transition: 0.2s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.45);
}

/* SECTION TITLE */
.section-title {
    background: linear-gradient(90deg, #6366f1, #22d3ee);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 1.2rem;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    border: none;
    padding: 0.8rem 1rem;
    border-radius: 12px;
    color: white !important;
    font-weight: 700;
    transition: 0.15s;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #2563eb, #0ea5e9);
    transform: scale(1.03);
}

/* OUTPUT BOX — BIG FONT */
.output-box {
    background: rgba(255,255,255,0.08);
    border-left: 6px solid #60a5fa;
    border-radius: 14px;
    padding: 1.6rem 1.7rem;
    color: #f9fafb;
    font-size: 1.25rem;
    line-height: 1.85rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.45);
}

.output-box ul {
    padding-left: 1.2rem;
}
.output-box li {
    margin-bottom: 0.7rem;
}

/* IMAGE */
.output-image {
    width: 100%;
    border-radius: 16px;
    margin-bottom: 1rem;
}

/* FOOTER */
.footer {
    text-align:center;
    padding:1rem;
    font-size:0.9rem;
    color:#9ca3af;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)



# -----------------------------------------------------
# ✅ Audio Extraction (FFmpeg)
# -----------------------------------------------------
def video_to_audio(video_path: str) -> str:
    out_wav = f"temp_{uuid.uuid4()}.wav"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        out_wav
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_wav


# -----------------------------------------------------
# ✅ Speech Recognition
# -----------------------------------------------------
def audio_to_text(audio_path):
    rec = sr.Recognizer()
    with sr.AudioFile(audio_path) as src:
        data = rec.record(src)
    return rec.recognize_google(data)


# -----------------------------------------------------
# ✅ Educational Notes (not video description)
# -----------------------------------------------------
def generate_notes(text):
    model = genai.GenerativeModel(MODEL_NAME)

    prompt = """
You are an expert teacher. The text below is a spoken lecture.

✅ Create meaningful, readable, student-friendly NOTES.
✅ DO NOT describe what is happening in the video.
✅ DO NOT narrate actions.
✅ Write ONLY the concepts, definitions, explanations, steps, examples.
✅ Make it perfect for studying.

Format:
- Clear bullet points
- Definitions
- Explanations
- Concepts
- Key ideas
- Important notes

Lecture content:
""" + text

    return model.generate_content(prompt).text


# -----------------------------------------------------
# ✅ Quiz Generator
# -----------------------------------------------------
def generate_quiz(text):
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = """
Create:
✅ 3 MCQs (4 options each)
✅ 1 short answer
✅ 1 true/false
""" + text
    return model.generate_content(prompt).text



# -----------------------------------------------------
# ✅ HERO HEADER
# -----------------------------------------------------
st.markdown("""
<div class='hero'>
    <h1>🎧 AI Notes & Quiz Generator</h1>
    <p>Upload any lecture — AI transcribes and creates smart, study-ready notes + quizzes.</p>
</div>
""", unsafe_allow_html=True)
st.write("")


# -----------------------------------------------------
# MAIN UI
# -----------------------------------------------------
left, right = st.columns([1.1, 1])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📤 Upload Your File</div>", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Supported: MP3 • WAV • MP4 • MKV • MOV",
        type=["mp3", "wav", "mp4", "mkv", "mov"]
    )
    run = st.button("⚡ Generate Notes & Quiz", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🚀 Process Flow</div>", unsafe_allow_html=True)
    st.write("✅ Upload → ✅ Extract → ✅ Transcribe → ✅ Notes → ✅ Quiz")
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------
# PROCESSING
# -----------------------------------------------------
if run:
    if not uploaded:
        st.warning("Please upload a file.")
    else:
        try:
            ext = uploaded.name.split(".")[-1]
            temp = f"temp.{ext}"
            with open(temp, "wb") as f:
                f.write(uploaded.getbuffer())

            # ✅ Extract audio if video
            if ext in ["mp4", "mkv", "mov"]:
                with st.spinner("🎬 Extracting audio..."):
                    audio = video_to_audio(temp)
            else:
                audio = temp

            # ✅ Convert audio to text
            with st.spinner("🎧 Transcribing..."):
                text_data = audio_to_text(audio)

            # ✅ Generate notes
            with st.spinner("📝 Generating study notes..."):
                notes = generate_notes(text_data)

            # ✅ Generate quiz
            with st.spinner("🧠 Creating quiz..."):
                quiz = generate_quiz(text_data)

            st.success("✅ Completed!")

            # -----------------------------------------------------
            # ✅ FORMAT BULLET POINTS
            # -----------------------------------------------------
            def html_list_format(text):
                text = text.replace("•", "<li>").replace("-", "<li>")
                return "<ul>" + text + "</ul>"

            formatted_notes = html_list_format(notes)
            formatted_quiz = html_list_format(quiz)

            # -----------------------------------------------------
            # ✅ CLEAN VERSION FOR DOWNLOAD
            # -----------------------------------------------------
            clean_notes = notes.replace("•", "- ").replace("<li>", "- ")
            clean_quiz = quiz.replace("•", "- ").replace("<li>", "- ")

            # -----------------------------------------------------
            # ✅ DISPLAY NOTES
            # -----------------------------------------------------
            st.markdown("## 📄 Study Notes")
            st.image(
                "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=1200",
                use_column_width=True
            )
            st.markdown(f"<div class='output-box'>{formatted_notes}</div>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Notes", clean_notes, "notes.txt")

            # -----------------------------------------------------
            # ✅ DISPLAY QUIZ
            # -----------------------------------------------------
            st.markdown("## 🧠 Quiz")
            st.image(
                "https://images.unsplash.com/photo-1553877522-43269d4ea984?q=80&w=1400",
                use_column_width=True
            )
            st.markdown(f"<div class='output-box'>{formatted_quiz}</div>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Quiz", clean_quiz, "quiz.txt")

        except Exception as e:
            st.error(f"Error: {e}")


# -----------------------------------------------------
# FOOTER
# -----------------------------------------------------
st.markdown("<div class='footer'>Built with ❤️ | Premium AI | Study Notes Engine</div>", unsafe_allow_html=True)
