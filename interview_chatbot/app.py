import os

import streamlit as st
import pandas as pd
import json
from groq import Groq
from database import init_db, save_interview, get_all_interviews

# =============================================
# =============================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Initialize Database
init_db()

# Page Config
st.set_page_config(page_title="AI Interview Assistant", page_icon="🤖", layout="wide")

# Load CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# =============================================
# STATE INITIALIZATION
# =============================================
defaults = {
    "page": "Setup",
    "history": [],
    "free_chat_history": [],
    "question_count": 0,
    "tech": "",
    "diff": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def reset_interview():
    st.session_state.history = []
    st.session_state.question_count = 0
    st.session_state.page = "Setup"
    if "feedback_generated" in st.session_state:
        del st.session_state.feedback_generated
    if "feedback_data" in st.session_state:
        del st.session_state.feedback_data


# =============================================
# GROQ AI HELPER
# =============================================
def get_ai_response(prompt, system_prompt="You are an expert technical interviewer."):
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_free_chat_response(messages):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=1024,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"


# =============================================
# SIDEBAR NAVIGATION
# =============================================
st.sidebar.title("🧭 Navigation")
nav = st.sidebar.radio("Go to", ["Interview Session", "Dashboard", "Free Chat"])

if nav == "Dashboard":
    st.session_state.page = "Dashboard"
elif nav == "Free Chat":
    st.session_state.page = "Free Chat"
elif nav == "Interview Session" and st.session_state.page in ["Dashboard", "Free Chat"]:
    st.session_state.page = "Setup"

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Powered by")
st.sidebar.markdown("**Groq API** (Free) + **Llama 3.1**")
st.sidebar.markdown("No GPU needed! ✅")

# =============================================
# HEADER
# =============================================
st.markdown("""
<div class="interview-header">
    <h1>🤖 AI Interview Assistant</h1>
    <p>Practice your tech interviews with Llama 3.1 via Groq — No GPU needed!</p>
</div>
""", unsafe_allow_html=True)


# =============================================
# PAGE: SETUP
# =============================================
if st.session_state.page == "Setup":
    st.subheader("⚙️ Interview Setup")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.tech = st.selectbox(
            "🖥️ Technology",
            ["Python", "JavaScript", "React Native", "Flutter",
             "Java", "C++", "SQL", "Machine Learning", "HR Interview"]
        )
    with col2:
        st.session_state.diff = st.selectbox(
            "📊 Difficulty",
            ["Beginner", "Intermediate", "Advanced"]
        )

    st.markdown("")
    if st.button("🚀 Start Interview", use_container_width=True):
        st.session_state.page = "Interview"
        st.session_state.history = []
        st.session_state.question_count = 1
        st.rerun()

    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        st.error("⚠️ Pehle app.py mein apni Groq API Key daalo! console.groq.com pe free mein milti hai.")


# =============================================
# PAGE: INTERVIEW
# =============================================
elif st.session_state.page == "Interview":
    st.subheader(f"📝 {st.session_state.tech} Interview — {st.session_state.diff} Level")

    if not st.session_state.history:
        with st.spinner("⏳ Generating first question..."):
            system_prompt = (
                f"You are a Senior Technical Interviewer conducting a "
                f"{st.session_state.diff} level interview on {st.session_state.tech}. "
                f"Ask ONE clear, professional interview question. Do not provide the answer. Be concise."
            )
            first_q = get_ai_response("Please ask the first interview question.", system_prompt)
            st.session_state.history.append({"role": "assistant", "content": first_q})

    for msg in st.session_state.history:
        if msg["role"] == "assistant":
            st.markdown(f"<div class='ai-message'><b>🤖 AI Interviewer:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='user-message'><b>👤 You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

    if st.session_state.question_count <= 5:
        st.markdown(f"**Question {st.session_state.question_count} of 5**")
        user_answer = st.text_area("✍️ Your Answer:", key=f"ans_{st.session_state.question_count}", height=120)

        col1, col2 = st.columns([3, 1])
        with col1:
            submit = st.button("✅ Submit Answer", use_container_width=True)
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                reset_interview()
                st.rerun()

        if submit:
            if user_answer.strip():
                st.session_state.history.append({"role": "user", "content": user_answer})

                if st.session_state.question_count < 5:
                    with st.spinner("🤔 Analyzing your answer..."):
                        system_prompt = (
                            f"You are a Senior Technical Interviewer. "
                            f"The candidate is being interviewed for {st.session_state.tech} ({st.session_state.diff} level). "
                            f"Give 1-2 lines of feedback on their last answer, then ask the NEXT interview question. "
                            f"Ask ONLY ONE question. Be concise and professional."
                        )
                        next_q = get_ai_response(
                            "Here is my answer. Please give brief feedback and ask the next question.",
                            system_prompt
                        )
                        st.session_state.history.append({"role": "assistant", "content": next_q})
                        st.session_state.question_count += 1
                        st.rerun()
                else:
                    st.session_state.page = "Feedback"
                    st.rerun()
            else:
                st.warning("⚠️ Pehle answer toh likho!")


# =============================================
# PAGE: FEEDBACK
# =============================================
elif st.session_state.page == "Feedback":
    st.subheader("🎯 Final Interview Feedback")

    if "feedback_generated" not in st.session_state:
        with st.spinner("📊 Generating your detailed feedback..."):
            system_prompt = (
                f"You are a Senior Technical Interviewer. Review the entire interview for "
                f"{st.session_state.tech} ({st.session_state.diff} level). "
                f"Respond ONLY with a valid JSON object. No extra text. Format:\n"
                f'{{ "score": <integer 1-10>, "strengths": "<text>", "weaknesses": "<text>", "improvement": "<text>" }}'
            )
            feedback_raw = get_ai_response(
                "The interview is complete. Provide final JSON assessment.",
                system_prompt
            )

            try:
                start_idx = feedback_raw.find("{")
                end_idx = feedback_raw.rfind("}") + 1
                feedback_json = json.loads(feedback_raw[start_idx:end_idx])
                st.session_state.feedback_data = feedback_json
                st.session_state.feedback_generated = True
                save_interview(
                    st.session_state.tech,
                    st.session_state.diff,
                    feedback_json.get("score", 0),
                    feedback_json.get("strengths", ""),
                    feedback_json.get("weaknesses", "")
                )
            except Exception as e:
                st.error(f"❌ Feedback parse nahi hua. Raw output:\n\n{feedback_raw}")

    if "feedback_data" in st.session_state:
        data = st.session_state.feedback_data
        score = data.get("score", 0)
        color = "#e74c3c" if score < 5 else "#f39c12" if score < 7 else "#2ecc71"

        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding: 2rem;">
            <h3>🏆 Overall Score</h3>
            <h2 style="font-size: 4rem; color: {color}; margin: 0;">{score} / 10</h2>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strengths")
            st.success(data.get("strengths", "N/A"))
        with col2:
            st.markdown("### 📉 Weaknesses")
            st.error(data.get("weaknesses", "N/A"))

        st.markdown("### 🚀 How to Improve")
        st.info(data.get("improvement", "N/A"))

        if st.button("🔁 Start New Interview", use_container_width=True):
            reset_interview()
            st.rerun()


# =============================================
# PAGE: DASHBOARD
# =============================================
elif st.session_state.page == "Dashboard":
    st.subheader("📊 Interview Dashboard")

    interviews = get_all_interviews()

    if not interviews:
        st.info("🙈  No interviews yet! Give your first interview..")
    else:
        df = pd.DataFrame(
            interviews,
            columns=["ID", "Date", "Technology", "Difficulty", "Score", "Strengths", "Weaknesses"]
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Total Interviews", len(df))
        with col2:
            st.metric("⭐ Average Score", f"{df['Score'].mean():.1f} / 10")
        with col3:
            st.metric("🏅 Best Score", f"{df['Score'].max()} / 10")

        st.markdown("### 📅 Interview History")
        display_df = df[["Date", "Technology", "Difficulty", "Score"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("### 🔍 Detailed History")
        for _, row in df.iterrows():
            with st.expander(f"📌 {row['Date']} — {row['Technology']} ({row['Difficulty']}) — Score: {row['Score']}/10"):
                st.write(f"**💪 Strengths:** {row['Strengths']}")
                st.write(f"**📉 Weaknesses:** {row['Weaknesses']}")


# =============================================
# PAGE: FREE CHAT
# =============================================
elif st.session_state.page == "Free Chat":
    st.subheader("💬 Free Chat with AI")
    st.markdown("Ask me anything  — interview prep, doubts, ya general tech questions!")

    for message in st.session_state.free_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.free_chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("thinking..."):
                reply = get_free_chat_response(st.session_state.free_chat_history)
                st.markdown(reply)
                st.session_state.free_chat_history.append({"role": "assistant", "content": reply})

    if st.session_state.free_chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.free_chat_history = []
            st.rerun()
