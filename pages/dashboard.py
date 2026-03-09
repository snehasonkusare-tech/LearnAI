import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_dashboard():
    topic = st.session_state.get("topic", "")
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")
    lesson_data = st.session_state.get("lesson_data")
    current_chapter = st.session_state.get("current_chapter", 0)
    quiz_score = st.session_state.get("quiz_score", 0)

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Dashboard</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">📊 Your Progress</div>
        <div class="hero-subtitle">Track your learning journey for <span style="color:#00d4ff;">{topic}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if not lesson_data:
        st.warning("No lesson started yet. Go to Home and start learning!")
        return

    chapters = lesson_data.get("chapters", [])
    total_chapters = len(chapters)
    completed = max(0, current_chapter - 1) if current_chapter > 0 else 0
    progress_pct = int((completed / total_chapters) * 100) if total_chapters > 0 else 0

    # Top stats
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        (completed, total_chapters, "Chapters Done", "#00d4ff"),
        (f"{progress_pct}%", "Completion", "Lesson Progress", "#7b61ff"),
        (quiz_score, "pts", "Quiz Score", "#00ff88"),
        (level, "", "Current Level", "#ffd700"),
    ]

    for col, (val, suffix, label, color) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:1.2rem; background:rgba(255,255,255,0.02);
                        border:1px solid {color}33; border-radius:12px;">
                <div style="color:{color}; font-size:1.8rem; font-weight:800; font-family:'Syne',sans-serif;">
                    {val}<span style="font-size:0.9rem; margin-left:2px;">{suffix}</span>
                </div>
                <div style="color:#8892a4; font-size:0.8rem; margin-top:0.3rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress bar
    st.markdown(f"""
    <div class="card">
        <div style="color:#ffffff; font-weight:700; margin-bottom:1rem;">📈 Overall Progress</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
            <span style="color:#8892a4; font-size:0.85rem;">{completed} of {total_chapters} chapters complete</span>
            <span style="color:#00d4ff; font-size:0.85rem; font-weight:600;">{progress_pct}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.05); border-radius:10px; height:10px; overflow:hidden;">
            <div style="height:10px; width:{progress_pct}%;
                        background:linear-gradient(90deg,#00d4ff,#7b61ff); border-radius:10px;
                        transition:width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chapter status grid
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="color:#ffffff; font-weight:700; margin-bottom:1rem;">📚 Chapter Breakdown</div>', unsafe_allow_html=True)

    for i, ch in enumerate(chapters):
        ch_num = ch.get("number", i + 1)
        ch_title = ch.get("title", f"Chapter {ch_num}")
        is_done = i < completed
        is_current = i == completed
        cache_exists = f"chapter_content_{i}" in st.session_state

        if is_done:
            status_color = "#00ff88"
            status_icon = "✅"
            status_text = "Completed"
        elif is_current:
            status_color = "#00d4ff"
            status_icon = "▶️"
            status_text = "In Progress"
        else:
            status_color = "#4a5568"
            status_icon = "🔒"
            status_text = "Not Started"

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:0.8rem 1rem; margin-bottom:0.5rem;
                    background:rgba(255,255,255,0.02); border-radius:8px;
                    border-left:3px solid {status_color};">
            <div>
                <span style="color:{status_color}; font-size:0.75rem; font-weight:600;
                             text-transform:uppercase; letter-spacing:1px;">Ch {ch_num}</span>
                <span style="color:#c9d3e0; font-size:0.9rem; margin-left:0.8rem;">{ch_title}</span>
            </div>
            <span style="color:{status_color}; font-size:0.8rem; white-space:nowrap;">
                {status_icon} {status_text}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Feature usage
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="color:#ffffff; font-weight:700; margin-bottom:1rem;">🛠️ Features Used</div>', unsafe_allow_html=True)

    features = [
        ("🤖 AI Doubt Solver", any(f"doubt_chat_" in k for k in st.session_state), "doubt_solver"),
        ("💪 Practice Problems", any(f"practice_" in k for k in st.session_state), "practice"),
        ("🃏 Flashcards", any(f"flashcards_" in k for k in st.session_state), "flashcards"),
        ("🎤 Mock Interview", any(f"interview_" in k for k in st.session_state), "interview"),
        ("📅 Study Plan", any(f"study_plan_" in k for k in st.session_state), "study_plan"),
        ("📄 Cheat Sheet", any(f"cheat_sheet_" in k for k in st.session_state), "cheat_sheet"),
    ]

    cols = st.columns(3)
    for idx, (fname, used, page_key) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="text-align:center; padding:1rem; background:{'rgba(0,255,136,0.08)' if used else 'rgba(255,255,255,0.02)'};
                        border:1px solid {'rgba(0,255,136,0.3)' if used else 'rgba(255,255,255,0.06)'};
                        border-radius:10px; margin-bottom:0.5rem;">
                <div style="font-size:1.2rem;">{fname.split()[0]}</div>
                <div style="color:{'#00ff88' if used else '#4a5568'}; font-size:0.75rem; margin-top:0.2rem;">
                    {'✅ Used' if used else '○ Not yet'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick links
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="color:#ffffff; font-weight:700; margin-bottom:1rem; font-size:1.1rem;">🚀 Jump To</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📖 Continue Lesson"):
            st.session_state.page = "lesson"
            st.rerun()
    with col2:
        if st.button("🧪 Take Quiz"):
            st.session_state.page = "quiz"
            st.rerun()
    with col3:
        if st.button("🏆 Certifications"):
            st.session_state.page = "certification"
            st.rerun()
