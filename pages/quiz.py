import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from utils.ai_utils import generate_quiz

def show_quiz():
    topic = st.session_state.topic
    language = st.session_state.language
    lesson_data = st.session_state.lesson_data

    # Back button
    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = "lesson"
            st.rerun()

    # Breadcrumb
    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Quiz</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">🧪 Knowledge Quiz</div>
        <div class="hero-subtitle">Test what you've learned — all questions based on your lesson</div>
    </div>
    """, unsafe_allow_html=True)

    # Generate quiz if not done
    if st.session_state.quiz_data is None:
        with st.spinner("📝 Generating your personalized quiz..."):
            quiz_data = generate_quiz(topic, lesson_data, language)
            if quiz_data:
                st.session_state.quiz_data = quiz_data
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
            else:
                st.error("Failed to generate quiz. Please try again.")
                return

    quiz_data = st.session_state.quiz_data
    questions = quiz_data.get("questions", [])

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    # Show questions
    for i, q in enumerate(questions):
        st.markdown(f"""
        <div class="card">
            <div class="quiz-counter">Question {i+1} of {len(questions)}</div>
            <div class="quiz-question">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        options = q.get("options", [])
        if not st.session_state.quiz_submitted:
            answer = st.radio(
                f"q_{i}",
                options,
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            st.session_state.quiz_answers[i] = options.index(answer) if answer in options else 0
        else:
            user_ans = st.session_state.quiz_answers.get(i, -1)
            correct_ans = q.get("correct", 0)
            for j, opt in enumerate(options):
                if j == correct_ans:
                    st.markdown(f'<div style="padding:0.7rem 1rem; background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.4); border-radius:8px; color:#00ff88; margin-bottom:0.4rem;">✅ {opt}</div>', unsafe_allow_html=True)
                elif j == user_ans and user_ans != correct_ans:
                    st.markdown(f'<div style="padding:0.7rem 1rem; background:rgba(255,107,107,0.1); border:1px solid rgba(255,107,107,0.4); border-radius:8px; color:#ff6b6b; margin-bottom:0.4rem;">❌ {opt}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="padding:0.7rem 1rem; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:8px; color:#8892a4; margin-bottom:0.4rem;">{opt}</div>', unsafe_allow_html=True)

            # Show explanation
            st.markdown(f'<div style="margin-top:0.8rem; padding:0.8rem 1rem; background:rgba(123,97,255,0.08); border-left:3px solid #7b61ff; border-radius:0 8px 8px 0; color:#c9d3e0; font-size:0.9rem;"><strong style="color:#7b61ff;">Explanation:</strong> {q.get("explanation", "")}</div>', unsafe_allow_html=True)

        st.markdown("---")

    # Submit / Results
    if not st.session_state.quiz_submitted:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 Submit Quiz", key="submit_quiz"):
                # Calculate score
                score = 0
                for i, q in enumerate(questions):
                    if st.session_state.quiz_answers.get(i) == q.get("correct", 0):
                        score += 1
                st.session_state.quiz_score = score
                st.session_state.quiz_submitted = True
                st.rerun()
    else:
        score = st.session_state.quiz_score
        total = len(questions)
        pct = int((score / total) * 100)

        # Score card
        if pct >= 80:
            grade_color = "#00ff88"
            grade_msg = "Excellent! You've mastered this topic! 🎉"
            grade_emoji = "🏆"
        elif pct >= 60:
            grade_color = "#00d4ff"
            grade_msg = "Good job! A bit more practice and you'll nail it!"
            grade_emoji = "👍"
        else:
            grade_color = "#ff6b6b"
            grade_msg = "Keep practicing! Review the chapters and try again."
            grade_emoji = "💪"

        st.markdown(f"""
        <div style="text-align:center; padding: 2rem; background: rgba(255,255,255,0.02);
                    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; margin: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{grade_emoji}</div>
            <div style="font-family: Syne, sans-serif; font-size: 4rem; font-weight: 800;
                        color: {grade_color}; line-height: 1;">{score}/{total}</div>
            <div style="color: {grade_color}; font-size: 1.2rem; font-weight: 600;
                        margin: 0.5rem 0;">{pct}% Score</div>
            <div style="color: #8892a4; font-size: 1rem;">{grade_msg}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Retry Quiz"):
                st.session_state.quiz_data = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = {}
                st.rerun()
        with col2:
            if st.button("📖 Review Lesson"):
                st.session_state.page = "lesson"
                st.session_state.current_chapter = 1
                st.rerun()
        with col3:
            if st.button("🏆 Get Certified →"):
                st.session_state.page = "certification"
                st.rerun()
