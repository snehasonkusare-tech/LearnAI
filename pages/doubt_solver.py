import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import ask_doubt

def show_doubt_solver():
    topic = st.session_state.get("topic", "")
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")
    lesson_data = st.session_state.get("lesson_data")

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → AI Doubt Solver</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">🤖 AI Doubt Solver</div>
        <div class="hero-subtitle">Ask anything — get instant, topic-specific answers</div>
    </div>
    """, unsafe_allow_html=True)

    # Chapter selector
    chapters = lesson_data.get("chapters", []) if lesson_data else []
    chapter_names = [f"Chapter {c['number']}: {c['title']}" for c in chapters]
    chapter_names.insert(0, f"General — {topic}")

    selected = st.selectbox("Which chapter are you asking about?", chapter_names)
    chapter_title = selected.split(": ", 1)[1] if ": " in selected else topic

    # Init chat history per chapter
    chat_key = f"doubt_chat_{chapter_title}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    chat_history = st.session_state[chat_key]

    # Display chat history
    if chat_history:
        st.markdown('<div style="margin-bottom:1rem;">', unsafe_allow_html=True)
        for msg in chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin-bottom:0.8rem;">
                    <div style="background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(123,97,255,0.15));
                                border:1px solid rgba(0,212,255,0.3); border-radius:12px 12px 0 12px;
                                padding:0.8rem 1.2rem; max-width:75%; color:#e2e8f0; font-size:0.95rem;">
                        💬 {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin-bottom:0.8rem;">
                    <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
                                border-radius:12px 12px 12px 0; padding:0.8rem 1.2rem;
                                max-width:80%; color:#c9d3e0; font-size:0.95rem; line-height:1.7;">
                        🧠 {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card" style="text-align:center; padding:2rem;">
            <div style="font-size:2rem; margin-bottom:0.8rem;">💡</div>
            <div style="color:#8892a4; font-size:1rem;">
                Ask me anything about <span style="color:#00d4ff;">{chapter_title}</span> in <span style="color:#7b61ff;">{topic}</span>
            </div>
            <div style="color:#4a5568; font-size:0.85rem; margin-top:0.5rem;">
                Examples: "Explain this with an example", "Why does this happen?", "What's the difference between X and Y?"
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Input
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        question = st.text_input("Your question", placeholder=f"Ask anything about {chapter_title}...", label_visibility="collapsed", key=f"doubt_input_{chapter_title}")
    with col_btn:
        ask_clicked = st.button("Ask 🚀", key="ask_btn")

    if ask_clicked and question.strip():
        with st.spinner("🧠 Thinking..."):
            answer = ask_doubt(topic, chapter_title, level, language, question.strip(), chat_history)
            st.session_state[chat_key].append({"role": "user", "content": question.strip()})
            st.session_state[chat_key].append({"role": "assistant", "content": answer})
            st.rerun()

    # Clear chat
    if chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state[chat_key] = []
            st.rerun()
