import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import generate_mock_interview, grade_interview_answer

def show_interview():
    topic = st.session_state.get("topic", "")
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Mock Interview</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">🎤 Mock Interview</div>
        <div class="hero-subtitle">Practice real interview questions — get AI feedback on your answers</div>
    </div>
    """, unsafe_allow_html=True)

    interview_key = f"interview_{topic}_{level}"

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 New Questions"):
            if interview_key in st.session_state:
                del st.session_state[interview_key]
            if f"interview_answers_{topic}" in st.session_state:
                del st.session_state[f"interview_answers_{topic}"]
            st.rerun()

    if interview_key not in st.session_state:
        with st.spinner(f"🎤 Preparing {level}-level {topic} interview questions..."):
            questions = generate_mock_interview(topic, level, language)
            st.session_state[interview_key] = questions

    questions = st.session_state[interview_key]
    if not questions:
        st.error("Could not generate questions. Try again.")
        return

    answers_key = f"interview_answers_{topic}"
    grades_key = f"interview_grades_{topic}"
    if answers_key not in st.session_state:
        st.session_state[answers_key] = {}
    if grades_key not in st.session_state:
        st.session_state[grades_key] = {}

    answers = st.session_state[answers_key]
    grades = st.session_state[grades_key]

    type_colors = {
        "Conceptual": "#00d4ff",
        "Practical": "#7b61ff",
        "Problem-Solving": "#ff6b6b",
        "Advanced": "#ffd700"
    }

    for i, q in enumerate(questions):
        q_type = q.get("type", "Conceptual")
        color = type_colors.get(q_type, "#00d4ff")

        st.markdown(f"""
        <div class="card" style="border-color:rgba({','.join(str(int(color.lstrip('#')[j:j+2],16)) for j in (0,2,4))},0.3);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                <span style="color:{color}; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">
                    Q{i+1} · {q_type}
                </span>
                {"<span style='color:#00ff88; font-size:0.8rem;'>✅ Answered</span>" if str(i) in grades else ""}
            </div>
            <div style="color:#e2e8f0; font-size:1.05rem; font-weight:500; line-height:1.7;">
                {q.get('question', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if str(i) not in grades:
            user_answer = st.text_area(
                f"Your answer to Q{i+1}",
                placeholder="Type your answer here... be as detailed as you can",
                key=f"answer_input_{i}",
                label_visibility="collapsed",
                height=100
            )

            if st.button(f"📤 Submit Answer", key=f"submit_{i}"):
                if user_answer.strip():
                    with st.spinner("🧠 Grading your answer..."):
                        grade = grade_interview_answer(
                            topic,
                            q.get("question", ""),
                            user_answer.strip(),
                            q.get("ideal_answer", ""),
                            language
                        )
                        answers[str(i)] = user_answer.strip()
                        grades[str(i)] = grade
                        st.rerun()
                else:
                    st.warning("Please type an answer before submitting.")
        else:
            grade = grades[str(i)]
            score = grade.get("score", 5)
            verdict = grade.get("verdict", "Good")
            verdict_colors = {"Excellent": "#00ff88", "Good": "#00d4ff", "Needs Work": "#ffd700", "Incorrect": "#ff6b6b"}
            v_color = verdict_colors.get(verdict, "#00d4ff")

            score_pct = (score / 10) * 100

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.08);
                        border-radius:12px; padding:1.2rem; margin-bottom:0.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <span style="color:#8892a4; font-size:0.85rem;">Your answer: <em style="color:#c9d3e0;">{answers.get(str(i), '')[:80]}...</em></span>
                    <span style="background:{v_color}22; color:{v_color}; border:1px solid {v_color}44;
                                 padding:0.2rem 0.8rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
                        {verdict} · {score}/10
                    </span>
                </div>
                <div style="background:rgba(255,255,255,0.05); border-radius:8px; height:6px; margin-bottom:1rem; overflow:hidden;">
                    <div style="height:6px; width:{score_pct}%; background:linear-gradient(90deg,{v_color},{v_color}88); border-radius:8px;"></div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin-bottom:0.8rem;">
                    <div style="background:rgba(0,255,136,0.06); border:1px solid rgba(0,255,136,0.15); border-radius:8px; padding:0.8rem;">
                        <div style="color:#00ff88; font-size:0.75rem; font-weight:700; margin-bottom:0.3rem;">✅ STRENGTHS</div>
                        <div style="color:#c9d3e0; font-size:0.85rem; line-height:1.6;">{grade.get('strengths', '')}</div>
                    </div>
                    <div style="background:rgba(255,107,107,0.06); border:1px solid rgba(255,107,107,0.15); border-radius:8px; padding:0.8rem;">
                        <div style="color:#ff6b6b; font-size:0.75rem; font-weight:700; margin-bottom:0.3rem;">🔧 IMPROVE</div>
                        <div style="color:#c9d3e0; font-size:0.85rem; line-height:1.6;">{grade.get('improvements', '')}</div>
                    </div>
                </div>
                <div style="background:rgba(255,215,0,0.06); border:1px solid rgba(255,215,0,0.15); border-radius:8px; padding:0.8rem;">
                    <span style="color:#ffd700; font-size:0.75rem; font-weight:700;">💡 TIP: </span>
                    <span style="color:#c9d3e0; font-size:0.85rem;">{grade.get('tip', '')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"👁️ See ideal answer for Q{i+1}"):
                st.markdown(f'<div style="color:#c9d3e0; line-height:1.7;">{q.get("ideal_answer", "")}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Final score
    if len(grades) == len(questions):
        total = sum(g.get("score", 5) for g in grades.values())
        avg = total / len(grades)
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align:center; padding:2rem; background:linear-gradient(135deg,rgba(0,212,255,0.1),rgba(123,97,255,0.1));
                    border:1px solid rgba(0,212,255,0.3); border-radius:16px; margin-top:1rem;">
            <div style="font-size:0.85rem; color:#8892a4; text-transform:uppercase; letter-spacing:2px; margin-bottom:0.5rem;">
                INTERVIEW COMPLETE
            </div>
            <div style="font-size:4rem; font-weight:800; background:linear-gradient(135deg,#00d4ff,#7b61ff);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.5rem;">
                {avg:.1f}/10
            </div>
            <div style="color:#c9d3e0; font-size:1rem;">
                {"🏆 Outstanding! You're interview-ready." if avg >= 8 else
                 "👍 Good performance! A bit more practice and you'll be ready." if avg >= 6 else
                 "📚 Keep studying and practicing — you're getting there!"}
            </div>
        </div>
        """, unsafe_allow_html=True)
