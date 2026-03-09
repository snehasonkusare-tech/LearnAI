import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

def show_home():
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🧠</div>
        <div class="hero-title">LearnAI</div>
        <div class="hero-subtitle">Your Personal AI Teacher — Any Topic, Any Language, Explained Simply</div>
    </div>
    """, unsafe_allow_html=True)

    # Feature pills
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 0.8rem; flex-wrap: wrap; margin-bottom: 3rem;">
        <span class="section-label label-explanation">✦ AI-Generated Lessons</span>
        <span class="section-label label-analogy">✦ Real-Life Examples</span>
        <span class="section-label label-example">✦ Visual Diagrams</span>
        <span class="section-label label-visual">✦ Certifications</span>
    </div>
    """, unsafe_allow_html=True)

    # Main input form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🚀 Start Learning</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-text" style="margin-bottom:1.5rem;">Enter any technology or concept and get a complete AI-generated lesson — no searching required.</div>', unsafe_allow_html=True)

        topic = st.text_input(
            "What do you want to learn?",
            placeholder="e.g. Neural Networks, Blockchain, Docker, Machine Learning...",
            key="topic_input"
        )

        level = st.selectbox(
            "Your Level",
            ["Beginner", "Intermediate", "Advanced"],
            key="level_input"
        )

        language = st.selectbox(
            "Preferred Language",
            [
                "English", "Hindi", "Urdu", "Arabic", "French",
                "Spanish", "German", "Portuguese", "Chinese (Simplified)",
                "Bengali", "Russian", "Japanese"
            ],
            key="language_input"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🎓 Generate My Lesson", key="generate_btn"):
            if topic.strip():
                new_topic = topic.strip()
                new_level = level
                new_language = language

                # If anything changed, wipe all cached content from previous topic
                if (new_topic != st.session_state.get("topic", "") or
                    new_level != st.session_state.get("level", "") or
                    new_language != st.session_state.get("language", "")):

                    keys_to_delete = [k for k in list(st.session_state.keys()) if any(k.startswith(p) for p in [
                        "chapter_content_",
                        "practice_",
                        "flashcards_",
                        "doubt_chat_",
                        "study_plan_",
                        "cheat_sheet_",
                        "interview_",
                        "interview_answers_",
                        "interview_grades_",
                        "reveal_",
                    ])]
                    for key in keys_to_delete:
                        del st.session_state[key]

                st.session_state.topic = new_topic
                st.session_state.level = new_level
                st.session_state.language = new_language
                st.session_state.page = "lesson"
                st.session_state.current_chapter = 0
                st.session_state.lesson_data = None
                st.session_state.quiz_data = None
                st.session_state.cert_data = None
                st.rerun()
            else:
                st.error("Please enter a topic to learn!")

        st.markdown('</div>', unsafe_allow_html=True)

    # How it works section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; font-family: Syne, sans-serif; font-size: 1.8rem; font-weight: 700; color: white; margin-bottom: 2rem;">How It Works</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("1", "📝", "Enter Topic", "Type any technology or concept you want to learn"),
        ("2", "🤖", "AI Generates", "Claude creates a full lesson plan with 5 chapters"),
        ("3", "🎨", "Visual Learning", "Animated diagrams, analogies & real examples"),
        ("4", "🏆", "Get Certified", "Get a personalized certification roadmap"),
    ]
    for col, (num, icon, title, desc) in zip([c1, c2, c3, c4], steps):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">{icon}</div>
                <div style="color:#00d4ff; font-size:0.75rem; font-weight:600; letter-spacing:2px; margin-bottom:0.3rem;">STEP {num}</div>
                <div class="card-title" style="font-size:1rem;">{title}</div>
                <div class="card-text" style="font-size:0.85rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
