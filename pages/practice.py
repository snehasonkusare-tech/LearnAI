import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import generate_practice_problems

def show_practice():
    topic = st.session_state.get("topic", "")
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")
    lesson_data = st.session_state.get("lesson_data")

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Practice Problems</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">💪 Practice Problems</div>
        <div class="hero-subtitle">AI-generated fresh problems — never the same twice</div>
    </div>
    """, unsafe_allow_html=True)

    chapters = lesson_data.get("chapters", []) if lesson_data else []
    chapter_names = [f"Chapter {c['number']}: {c['title']}" for c in chapters]

    if not chapter_names:
        st.warning("Please complete at least one chapter first.")
        return

    selected = st.selectbox("Choose a chapter to practice", chapter_names)
    chapter_title = selected.split(": ", 1)[1] if ": " in selected else topic

    cache_key = f"practice_{chapter_title}"

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 New Problems", key="regen_problems"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()

    if cache_key not in st.session_state:
        with st.spinner(f"⚙️ Generating 5 problems for {chapter_title}..."):
            problems = generate_practice_problems(topic, chapter_title, level, language)
            st.session_state[cache_key] = problems

    problems = st.session_state[cache_key]

    if not problems:
        st.error("Could not generate problems. Try again.")
        return

    # Track revealed hints/answers
    if f"reveal_{cache_key}" not in st.session_state:
        st.session_state[f"reveal_{cache_key}"] = {}

    reveal_state = st.session_state[f"reveal_{cache_key}"]

    for i, prob in enumerate(problems):
        difficulty_colors = ["#00d4ff", "#7b61ff", "#ff6b6b", "#ffd700", "#00ff88"]
        difficulty_labels = ["Warm Up", "Easy", "Medium", "Hard", "Challenge"]
        color = difficulty_colors[i % len(difficulty_colors)]
        label = difficulty_labels[i % len(difficulty_labels)]

        st.markdown(f"""
        <div class="card" style="border-color:rgba({','.join(str(int(color.lstrip('#')[j:j+2], 16)) for j in (0,2,4))},0.3);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="color:{color}; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">
                    Problem {i+1}
                </span>
                <span style="background:rgba({','.join(str(int(color.lstrip('#')[j:j+2], 16)) for j in (0,2,4))},0.15);
                             color:{color}; padding:0.2rem 0.8rem; border-radius:20px; font-size:0.75rem; font-weight:600;">
                    {label}
                </span>
            </div>
            <div style="color:#e2e8f0; font-size:1rem; line-height:1.7; margin-bottom:1.2rem;">
                {prob.get('problem', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_hint, col_ans, col_space = st.columns([1, 1, 2])
        with col_hint:
            if st.button(f"💡 Hint", key=f"hint_{i}_{cache_key}"):
                reveal_state[f"hint_{i}"] = not reveal_state.get(f"hint_{i}", False)
                st.rerun()
        with col_ans:
            if st.button(f"✅ Answer", key=f"ans_{i}_{cache_key}"):
                reveal_state[f"ans_{i}"] = not reveal_state.get(f"ans_{i}", False)
                st.rerun()

        if reveal_state.get(f"hint_{i}"):
            st.markdown(f"""
            <div style="background:rgba(255,215,0,0.08); border:1px solid rgba(255,215,0,0.2);
                        border-radius:10px; padding:1rem; margin-bottom:0.5rem;">
                <span style="color:#ffd700; font-weight:700; font-size:0.85rem;">💡 HINT</span><br>
                <span style="color:#c9d3e0; font-size:0.95rem;">{prob.get('hint', '')}</span>
            </div>
            """, unsafe_allow_html=True)

        if reveal_state.get(f"ans_{i}"):
            st.markdown(f"""
            <div style="background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.2);
                        border-radius:10px; padding:1rem; margin-bottom:1rem;">
                <span style="color:#00ff88; font-weight:700; font-size:0.85rem;">✅ ANSWER</span><br>
                <span style="color:#c9d3e0; font-size:0.95rem; line-height:1.7;">{prob.get('answer', '')}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
