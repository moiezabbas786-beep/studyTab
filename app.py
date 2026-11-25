import time
import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="StudyTap AI", page_icon="⚡", layout="centered")
st.title("⚡ StudyTap AI Revision Coach")

tab1, tab2 = st.tabs(["⏱️ 1. Focus Timer", "📸 2. AI Snap-to-Quiz"])

with tab1:
    st.subheader("Phone-Free Focus Block")
    options = (1, 25, 45)
    mins = st.radio("Choose session length:", options, horizontal=True, format_func=lambda x: f"{x} mins")
    if st.button("Start Focus Countdown ▶️", type="primary"):
        placeholder = st.empty()
        for remaining in range(mins * 60, -1, -1):
            m, s = divmod(remaining, 60)
            placeholder.markdown(f"<h1 style='text-align: center; font-size: 64px;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        st.success("🎉 Time's up! Switch to the 'AI Snap-to-Quiz' tab!")

with tab2:
    st.subheader("Turn Your Notes Into an Exam Quiz")
    board = st.selectbox("Select your UK Exam Board:", ["AQA", "Edexcel", "OCR", "WJEC"])
    photo = st.camera_input("Snap a photo of your textbook or notes") or st.file_uploader("Or upload a photo", type=["jpg", "png", "jpeg"])
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if photo and api_key:
        img = Image.open(photo)
        st.image(img, caption="Notes Captured", use_container_width=True)
        if st.button("Generate 5 Exam Questions 🚀", type="primary"):
            with st.spinner(f"Creating {board}-style questions..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"You are a strict UK {board} GCSE/A-Level examiner. Look at this photo of a student's textbook or revision notes. Write 5 active-recall exam questions based ONLY on this photo using official {board} command words. List Questions 1 to 5 first, then put '---' and list the Mark Scheme Answers below."
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[img, prompt]
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"API Error: {e}")
