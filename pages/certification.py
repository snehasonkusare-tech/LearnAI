import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from utils.ai_utils import generate_certification_roadmap

def show_certification():
    topic = st.session_state.topic
    level = st.session_state.level
    language = st.session_state.language

    # Back button
    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = "quiz"
            st.rerun()

    # Breadcrumb
    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Certifications</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">🏆 Certification Roadmap</div>
        <div class="hero-subtitle">Your personalized path to professional recognition</div>
    </div>
    """, unsafe_allow_html=True)

    # Generate cert data
    if st.session_state.cert_data is None:
        with st.spinner("🔍 Finding the best certifications for you..."):
            cert_data = generate_certification_roadmap(topic, level, language)
            if cert_data:
                st.session_state.cert_data = cert_data
            else:
                st.error("Failed to generate certification roadmap. Please try again.")
                return

    cert_data = st.session_state.cert_data
    certifications = cert_data.get("certifications", [])
    roadmap_steps = cert_data.get("roadmap_steps", [])
    recommended_first = cert_data.get("recommended_first", "")
    total_time = cert_data.get("total_time", "")

    # Summary bar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <div style="font-size:2rem; margin-bottom:0.3rem;">📜</div>
            <div style="color:#ffd700; font-size:1.8rem; font-weight:800; font-family:Syne,sans-serif;">{len(certifications)}</div>
            <div style="color:#8892a4; font-size:0.9rem;">Certifications Found</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <div style="font-size:2rem; margin-bottom:0.3rem;">⏱️</div>
            <div style="color:#00d4ff; font-size:1.1rem; font-weight:700; font-family:Syne,sans-serif;">{total_time}</div>
            <div style="color:#8892a4; font-size:0.9rem;">To First Certification</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <div style="font-size:2rem; margin-bottom:0.3rem;">⭐</div>
            <div style="color:#00ff88; font-size:1rem; font-weight:700; font-family:Syne,sans-serif;">{recommended_first[:30]}...</div>
            <div style="color:#8892a4; font-size:0.9rem;">Best to Start With</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Certifications list
    st.markdown('<div class="card-title" style="font-size:1.5rem; margin-bottom:1.5rem;">📜 Available Certifications</div>', unsafe_allow_html=True)

    for cert in certifications:
        level_colors = {
            "Beginner": "#00ff88",
            "Intermediate": "#00d4ff",
            "Advanced": "#ff6b6b"
        }
        cert_level = cert.get("level", "Intermediate")
        color = level_colors.get(cert_level, "#7b61ff")

        is_recommended = recommended_first.lower() in cert.get("name", "").lower()

        border_style = "border: 1px solid rgba(255,215,0,0.4);" if is_recommended else "border: 1px solid rgba(255,255,255,0.08);"

        st.markdown(f"""
        <div class="cert-card" style="{border_style}">
            {'<div style="color:#ffd700; font-size:0.75rem; font-weight:700; margin-bottom:0.5rem;">⭐ RECOMMENDED FOR YOU</div>' if is_recommended else ''}
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
                <div>
                    <span class="cert-badge">{cert.get('provider', '')}</span>
                    <div class="cert-name">{cert.get('name', '')}</div>
                    <div class="cert-desc">{cert.get('description', '')}</div>
                </div>
                <div style="text-align:right; flex-shrink:0;">
                    <div style="color:{color}; font-weight:700; font-size:0.9rem; margin-bottom:0.3rem;">{cert_level}</div>
                    <div style="color:#8892a4; font-size:0.8rem;">⏱ {cert.get('time_estimate', '')}</div>
                    <div style="color:#ffd700; font-size:0.8rem; margin-top:0.2rem;">💰 {cert.get('cost', '')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Roadmap Steps
    st.markdown('<div class="card-title" style="font-size:1.5rem; margin-bottom:1.5rem;">🗺️ Your Learning Roadmap</div>', unsafe_allow_html=True)

    for i, step in enumerate(roadmap_steps):
        st.markdown(f"""
        <div class="roadmap-step">
            <div class="step-number">{i+1}</div>
            <div class="step-text">{step}</div>
        </div>
        """, unsafe_allow_html=True)

    # Free Resources
    free_resources = cert_data.get("free_resources", [])
    if free_resources:
        st.markdown("---")
        st.markdown('<div class="card-title" style="font-size:1.5rem; margin-bottom:1.5rem;">🆓 Free Learning Resources</div>', unsafe_allow_html=True)
        for resource in free_resources:
            st.markdown(f"""
            <div style="padding:0.9rem 1.2rem; background:rgba(0,255,136,0.05);
                        border:1px solid rgba(0,255,136,0.2); border-radius:10px; margin-bottom:0.7rem;">
                <span style="color:#00ff88; font-size:1rem;">✦</span>
                <span style="color:#c9d3e0; font-size:0.95rem; margin-left:0.5rem;">{resource}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Final action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Learn New Topic"):
            st.session_state.page = "home"
            st.session_state.lesson_data = None
            st.session_state.quiz_data = None
            st.session_state.cert_data = None
            st.session_state.topic = ""
            st.rerun()
    with col2:
        if st.button("📖 Review Lesson"):
            st.session_state.page = "lesson"
            st.session_state.current_chapter = 1
            st.rerun()
    with col3:
        if st.button("🧪 Retake Quiz"):
            st.session_state.page = "quiz"
            st.session_state.quiz_data = None
            st.session_state.quiz_submitted = False
            st.rerun()
