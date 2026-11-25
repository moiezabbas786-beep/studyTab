import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image

st.set_page_config(page_title="StudyTap AI", page_icon="⚡", layout="centered")
st.title("⚡ StudyTap AI Revision Coach")

api_key = st.secrets.get("GEMINI_API_KEY", "")

tab1, tab2, tab3 = st.tabs(["⏱️ Focus Timer", "📸 Snap-to-Quiz", "🤖 AI Exam Tutor"])

# --- TAB 1: STRICT FOCUS TIMER ---
with tab1:
    st.subheader("Phone-Free Strict Focus Mode")
    st.write("Start your timer and keep this screen open. **If you switch to TikTok, WhatsApp, or another app, your session fails and resets!**")
    
    options = (1, 25, 45)
    mins = st.radio("Choose session length:", options, horizontal=True, format_func=lambda x: f"{x} mins")

    timer_html = f"""
    <div id="box" style="font-family: sans-serif; text-align: center; padding: 24px; border-radius: 16px; background: #161b22; color: white; border: 2px solid #30363d;">
        <div id="status" style="font-size: 16px; color: #8b949e; margin-bottom: 8px;">Ready to lock in</div>
        <div id="clock" style="font-size: 64px; font-weight: bold; letter-spacing: 2px; margin: 10px 0;">{mins:02d}:00</div>
        <button id="startBtn" onclick="startTimer()" style="background: #ff4b4b; color: white; border: none; padding: 14px 28px; font-size: 18px; font-weight: bold; border-radius: 10px; cursor: pointer; margin-top: 10px;">
            Lock In & Start ▶️
        </button>
    </div>

    <script>
        let totalSeconds = {mins} * 60;
        let remaining = totalSeconds;
        let running = false;
        let interval = null;

        function updateDisplay() {{
            let m = Math.floor(remaining / 60);
            let s = remaining % 60;
            document.getElementById("clock").innerText = String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0');
        }}

        function playBeep(freq, duration) {{
            try {{
                let ctx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = ctx.createOscillator();
                osc.frequency.value = freq;
                osc.connect(ctx.destination);
                osc.start();
                setTimeout(() => osc.stop(), duration);
            }} catch(e) {{}}
        }}

        function startTimer() {{
            if (running) return;
            running = true;
            remaining = totalSeconds;
            updateDisplay();
            document.getElementById("box").style.borderColor = "#1f6feb";
            document.getElementById("status").innerText = "🔒 STRICT MODE ACTIVE — Do not leave this screen!";
            document.getElementById("status").style.color = "#58a6ff";
            document.getElementById("startBtn").style.display = "none";

            interval = setInterval(() => {{
                remaining--;
                updateDisplay();
                if (remaining <= 0) {{
                    clearInterval(interval);
                    running = false;
                    document.getElementById("box").style.borderColor = "#2ea043";
                    document.getElementById("status").innerText = "🎉 COMPLETE! Tap '📸 Snap-to-Quiz' above to test yourself!";
                    document.getElementById("status").style.color = "#3fb950";
                    document.getElementById("startBtn").innerText = "Start Another Session 🔄";
                    document.getElementById("startBtn").style.display = "inline-block";
                    playBeep(880, 400);
                }}
            }}, 1000);
        }}

        document.addEventListener("visibilitychange", () => {{
            if (document.hidden && running) {{
                clearInterval(interval);
                running = false;
                remaining = totalSeconds;
                updateDisplay();
                document.getElementById("box").style.borderColor = "#da3633";
                document.getElementById("status").innerText = "❌ FOCUS BROKEN! You left the app — timer reset!";
                document.getElementById("status").style.color = "#f85149";
                document.getElementById("startBtn").innerText = "Try Again 🔄";
                document.getElementById("startBtn").style.display = "inline-block";
                playBeep(220, 500);
            }}
        }});
    </script>
    """
    components.html(timer_html, height=260)

# --- TAB 2: AI PHOTO-TO-QUIZ + AI MARKING ---
with tab2:
    st.subheader("Turn Your Notes Into an Exam Quiz")
    board = st.selectbox("Select your UK Exam Board:", ["AQA", "Edexcel", "OCR", "WJEC"], key="quiz_board")
    photo = st.file_uploader("📸 Tap to Take Photo (with Zoom) or Upload Notes", type=["jpg", "png", "jpeg"])

    if photo and api_key:
        img = Image.open(photo)
        st.image(img, caption="Notes Captured", use_container_width=True)
        if st.button("Generate 5 Exam Questions 🚀", type="primary"):
            with st.spinner(f"Creating {board}-style questions..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"You are a strict UK {board} GCSE/A-Level examiner. Look at this photo of a student's textbook or revision notes. Write 5 numbered active-recall exam questions based ONLY on this photo using official {board} command words. Do NOT include the answers yet so the student can try answering them first!"
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=[img, prompt]
                    )
                    st.session_state["quiz_questions"] = response.text
                except Exception as e:
                    st.error(f"API Error: {e}")

    if "quiz_questions" in st.session_state:
        st.markdown("### 📝 Your Exam Questions")
        st.markdown(st.session_state["quiz_questions"])
        
        user_answers = st.text_area("Type your answers below (e.g., 1. ... 2. ...) and let the AI Examiner grade you:")
        if st.button("Mark My Answers ✅"):
            if user_answers.strip():
                with st.spinner("AI Examiner is grading your work..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        grade_prompt = f"""
                        You are a UK {board} examiner. Here were the 5 questions:
                        {st.session_state['quiz_questions']}
                        
                        Here are the student's answers:
                        {user_answers}
                        
                        Grade each answer (Correct / Partially Correct / Incorrect), give a final score out of 5, and show the exact official {board} mark-scheme answer for each question.
                        """
                        grade_res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=grade_prompt
                        )
                        st.markdown("### 🏆 Examiner Feedback")
                        st.markdown(grade_res.text)
                    except Exception as e:
                        st.error(f"API Error: {e}")

# --- TAB 3: AI EXAM TUTOR CHAT ---
with tab3:
    st.subheader("🤖 Ask Your AI GCSE/A-Level Tutor")
    tutor_board = st.selectbox("Exam Board:", ["AQA", "Edexcel", "OCR", "WJEC"], key="tutor_board")
    subject = st.text_input("Subject (e.g. GCSE Biology, Computer Science, History):", value="GCSE Computer Science")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything or ask for a practice exam question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = genai.Client(api_key=api_key)
                    tutor_prompt = f"You are a friendly, sharp UK {tutor_board} {subject} tutor helping a secondary school student revise. Keep explanations clear, concise, and focused on UK exam mark schemes. Student says: {prompt}"
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=tutor_prompt
                    )
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"API Error: {e}")
