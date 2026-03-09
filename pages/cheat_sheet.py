import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import generate_cheat_sheet

def show_cheat_sheet():
    topic = st.session_state.get("topic", "")
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")
    lesson_data = st.session_state.get("lesson_data")

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Cheat Sheet</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">📄 Cheat Sheet</div>
        <div class="hero-subtitle">Everything you learned — condensed into one quick reference</div>
    </div>
    """, unsafe_allow_html=True)

    if not lesson_data:
        st.warning("Please generate a lesson first.")
        return

    sheet_key = f"cheat_sheet_{topic}_{level}"

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Regenerate"):
            if sheet_key in st.session_state:
                del st.session_state[sheet_key]
            st.rerun()

    if sheet_key not in st.session_state:
        with st.spinner(f"📄 Generating your {topic} cheat sheet..."):
            sheet = generate_cheat_sheet(topic, level, language, lesson_data)
            st.session_state[sheet_key] = sheet

    sheet = st.session_state.get(sheet_key, "")

    if not sheet:
        st.error("Could not generate cheat sheet. Try again.")
        return

    # Render cheat sheet nicely
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(0,212,255,0.2);
                border-radius:16px; padding:2rem; margin-bottom:1.5rem;">
        <div style="text-align:center; margin-bottom:1.5rem;">
            <div style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#00d4ff,#7b61ff);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                {topic} — {level} Level
            </div>
            <div style="color:#4a5568; font-size:0.85rem; margin-top:0.3rem;">Quick Reference Cheat Sheet</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Parse sections and render
    lines = sheet.strip().split('\n')
    current_section = []
    sections = []
    current_heading = None

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('## ') or line_stripped.startswith('### '):
            if current_heading and current_section:
                sections.append((current_heading, '\n'.join(current_section)))
            current_heading = line_stripped.lstrip('#').strip()
            current_section = []
        elif current_heading:
            current_section.append(line)

    if current_heading and current_section:
        sections.append((current_heading, '\n'.join(current_section)))

    section_colors = ["#00d4ff", "#7b61ff", "#ff6b6b", "#00ff88", "#ffd700", "#ff9500"]

    if sections:
        for idx, (heading, content) in enumerate(sections):
            color = section_colors[idx % len(section_colors)]
            content_lines = [l.strip() for l in content.strip().split('\n') if l.strip()]
            content_html = ""
            for cl in content_lines:
                if cl.startswith('- ') or cl.startswith('• '):
                    content_html += f'<div style="padding:0.3rem 0; color:#c9d3e0; font-size:0.95rem; line-height:1.6; padding-left:1rem;">▸ {cl[2:]}</div>'
                elif cl.startswith('**') and cl.endswith('**'):
                    content_html += f'<div style="color:#ffffff; font-weight:700; font-size:0.95rem; margin-top:0.5rem;">{cl[2:-2]}</div>'
                else:
                    content_html += f'<div style="color:#c9d3e0; font-size:0.95rem; line-height:1.7; margin-bottom:0.3rem;">{cl}</div>'

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02); border-left:4px solid {color};
                        border-radius:0 12px 12px 0; padding:1.2rem 1.5rem; margin-bottom:1rem;">
                <div style="color:{color}; font-weight:700; font-size:0.9rem; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:0.8rem;">
                    {heading}
                </div>
                {content_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        # Render as plain text if no sections found
        paras = [p.strip() for p in sheet.split('\n') if p.strip()]
        for para in paras:
            st.markdown(f'<p style="color:#c9d3e0; line-height:1.8; margin-bottom:0.6rem;">{para}</p>', unsafe_allow_html=True)

    # Copy button
    st.markdown("<br>", unsafe_allow_html=True)
    st.text_area("📋 Copy raw cheat sheet text", value=sheet, height=200, key="cheat_sheet_copy")
