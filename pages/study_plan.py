import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import generate_study_plan

def show_study_plan():
    topic = st.session_state.get("topic", "")
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")
    lesson_data = st.session_state.get("lesson_data")

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Study Plan</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">📅 Study Plan Generator</div>
        <div class="hero-subtitle">Tell us your time — we build your personal schedule</div>
    </div>
    """, unsafe_allow_html=True)

    if not lesson_data:
        st.warning("Please generate a lesson first from the Home page.")
        return

    # Input form
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ Your Schedule</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("How many days do you have?", min_value=3, max_value=60, value=14, step=1)
    with col2:
        hours = st.slider("Hours per day you can study", min_value=0.5, max_value=8.0, value=1.0, step=0.5)

    total_hours = days * hours
    chapters = lesson_data.get("chapters", [])
    st.markdown(f"""
    <div style="margin-top:1rem; padding:1rem; background:rgba(0,212,255,0.08);
                border-radius:10px; border:1px solid rgba(0,212,255,0.2);">
        <span style="color:#00d4ff; font-weight:600;">📊 Summary:</span>
        <span style="color:#c9d3e0; margin-left:0.5rem;">
            {days} days × {hours} hrs = <strong style="color:#00d4ff;">{total_hours:.0f} total hours</strong>
            to cover <strong style="color:#7b61ff;">{len(chapters)} chapters</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    plan_key = f"study_plan_{topic}_{days}_{hours}"

    if st.button("📅 Generate My Study Plan", key="gen_plan"):
        # Clear any previously stored plans for this topic
        keys_to_del = [k for k in list(st.session_state.keys()) if k.startswith("study_plan_")]
        for k in keys_to_del:
            del st.session_state[k]
        with st.spinner("📅 Building your personalized study plan..."):
            plan = generate_study_plan(topic, level, language, days, hours, lesson_data)
            if not plan:
                # Fallback: build a simple day-by-day plan from chapters
                plan = []
                chapters = lesson_data.get("chapters", [])
                chapters_per_day = max(1, len(chapters) // days)
                for d in range(1, days + 1):
                    ch_index = (d - 1) * chapters_per_day
                    ch = chapters[ch_index] if ch_index < len(chapters) else chapters[-1]
                    plan.append({
                        "day": str(d),
                        "focus": ch["title"],
                        "tasks": f"Read and study Chapter {ch['number']}: {ch['title']}. Take notes, review key concepts, and try to explain it in your own words.",
                        "goal": f"Understand the core ideas of {ch['title']} in {topic}."
                    })
            st.session_state[plan_key] = plan

    plan = st.session_state.get(plan_key, [])
    if not plan:
        st.info("Click **Generate My Study Plan** above to create your schedule.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-title" style="margin-bottom:1.5rem;">🗓️ Your Day-by-Day Plan</div>', unsafe_allow_html=True)

    day_colors = ["#00d4ff", "#7b61ff", "#ff6b6b", "#00ff88", "#ffd700", "#ff9500"]

    for i, day in enumerate(plan):
        color = day_colors[i % len(day_colors)]
        day_num = day.get("day", str(i + 1))
        focus = day.get("focus", "")
        tasks = day.get("tasks", "")
        goal = day.get("goal", "")

        st.markdown(f"""
        <div style="display:flex; gap:1.2rem; margin-bottom:1.2rem; padding:1.2rem;
                    background:rgba(255,255,255,0.02); border-radius:12px;
                    border-left:4px solid {color};">
            <div style="min-width:60px; text-align:center;">
                <div style="background:linear-gradient(135deg,{color}22,{color}11);
                            border:1px solid {color}44; border-radius:10px;
                            padding:0.5rem; color:{color}; font-weight:800; font-size:0.9rem;">
                    DAY<br>{day_num}
                </div>
            </div>
            <div style="flex:1;">
                <div style="color:{color}; font-weight:700; font-size:0.95rem; margin-bottom:0.4rem;">
                    📚 {focus}
                </div>
                <div style="color:#c9d3e0; font-size:0.9rem; line-height:1.7; margin-bottom:0.4rem;">
                    {tasks}
                </div>
                {f'<div style="color:#8892a4; font-size:0.85rem;">🎯 Goal: {goal}</div>' if goal else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Link to the chapter mentioned in this day's focus
        import re as _re
        chapter_match = _re.search(r'chapter\s*(\d+)', focus, _re.IGNORECASE)
        if chapter_match:
            ch_num = int(chapter_match.group(1))
            if st.button(f"📖 Go to Chapter {ch_num}", key=f"goto_ch_{i}"):
                st.session_state.page = "lesson"
                st.session_state.current_chapter = ch_num
                st.rerun()

    # Summary stats
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:1.2rem; background:rgba(0,212,255,0.08);
                    border-radius:12px; border:1px solid rgba(0,212,255,0.2);">
            <div style="color:#00d4ff; font-size:2rem; font-weight:800;">{len(plan)}</div>
            <div style="color:#8892a4; font-size:0.85rem;">Study Days</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:1.2rem; background:rgba(123,97,255,0.08);
                    border-radius:12px; border:1px solid rgba(123,97,255,0.2);">
            <div style="color:#7b61ff; font-size:2rem; font-weight:800;">{total_hours:.0f}h</div>
            <div style="color:#8892a4; font-size:0.85rem;">Total Study Hours</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="text-align:center; padding:1.2rem; background:rgba(0,255,136,0.08);
                    border-radius:12px; border:1px solid rgba(0,255,136,0.2);">
            <div style="color:#00ff88; font-size:2rem; font-weight:800;">{len(chapters)}</div>
            <div style="color:#8892a4; font-size:0.85rem;">Chapters Covered</div>
        </div>
        """, unsafe_allow_html=True)
