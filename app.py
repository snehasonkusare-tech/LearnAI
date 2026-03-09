import streamlit as st

st.set_page_config(
    page_title="LearnAI - Your Personal AI Teacher",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import pages
from pages.home import show_home
from pages.lesson import show_lesson
from pages.quiz import show_quiz
from pages.certification import show_certification
from pages.doubt_solver import show_doubt_solver
from pages.practice import show_practice
from pages.flashcards import show_flashcards
from pages.study_plan import show_study_plan
from pages.interview import show_interview
from pages.cheat_sheet import show_cheat_sheet
from pages.dashboard import show_dashboard

# Initialize session state
defaults = {
    "page": "home", "topic": "", "level": "Beginner", "language": "English",
    "lesson_data": None, "quiz_data": None, "cert_data": None,
    "current_chapter": 0, "quiz_score": 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 50%, #0a0f1e 100%);
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main container */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
    }

    /* Hero Title */
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7b61ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #8892a4;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .card:hover {
        border-color: rgba(0, 212, 255, 0.3);
        background: rgba(0, 212, 255, 0.03);
    }

    .card-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .card-text {
        color: #8892a4;
        line-height: 1.7;
        font-size: 1rem;
    }

    /* Chapter cards */
    .chapter-card {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .chapter-number {
        font-size: 0.8rem;
        color: #00d4ff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.4rem;
    }

    .chapter-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* Section Labels */
    .section-label {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.8rem;
    }

    .label-explanation {
        background: rgba(0, 212, 255, 0.15);
        color: #00d4ff;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }

    .label-analogy {
        background: rgba(255, 107, 107, 0.15);
        color: #ff6b6b;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }

    .label-example {
        background: rgba(123, 97, 255, 0.15);
        color: #7b61ff;
        border: 1px solid rgba(123, 97, 255, 0.3);
    }

    .label-visual {
        background: rgba(0, 255, 136, 0.15);
        color: #00ff88;
        border: 1px solid rgba(0, 255, 136, 0.3);
    }

    /* Content text */
    .content-text {
        color: #c9d3e0;
        line-height: 1.8;
        font-size: 1.05rem;
    }

    /* Quiz styles */
    .quiz-question {
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1.5rem;
    }

    .quiz-counter {
        font-size: 0.85rem;
        color: #00d4ff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
    }

    /* Progress bar */
    .progress-container {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        height: 6px;
        margin-bottom: 2rem;
        overflow: hidden;
    }

    /* Cert card */
    .cert-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .cert-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        background: rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 20px;
        color: #ffd700;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.6rem;
    }

    .cert-name {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.4rem;
    }

    .cert-desc {
        color: #8892a4;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Step roadmap */
    .roadmap-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.2rem;
        padding: 1rem;
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        border-left: 3px solid #00d4ff;
    }

    .step-number {
        background: linear-gradient(135deg, #00d4ff, #7b61ff);
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .step-text {
        color: #c9d3e0;
        line-height: 1.6;
    }

    /* Streamlit button overrides */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #7b61ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: white !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1rem !important;
        padding: 0.8rem 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(0, 212, 255, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.1) !important;
    }

    /* Select box */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: white !important;
    }

    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }

    .stRadio > div > label {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        padding: 0.8rem 1.2rem !important;
        color: #c9d3e0 !important;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
    }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
        margin: 2rem 0 !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #00d4ff !important;
    }

    /* Success/Error boxes */
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 10px !important;
    }

    .stError {
        background: rgba(255, 107, 107, 0.1) !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
        border-radius: 10px !important;
    }

    /* Visual box */
    .visual-box {
        background: rgba(0, 255, 136, 0.03);
        border: 1px solid rgba(0, 255, 136, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        font-family: monospace;
        color: #00ff88;
        line-height: 1.8;
        font-size: 0.95rem;
        white-space: pre-wrap;
    }

    /* Nav breadcrumb */
    .nav-breadcrumb {
        font-size: 0.85rem;
        color: #4a5568;
        margin-bottom: 2rem;
    }

    .nav-breadcrumb span {
        color: #00d4ff;
    }

    /* Score display */
    .score-display {
        font-family: 'Syne', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #7b61ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }

    /* Metric override */
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-family: 'Syne', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation (only when a topic is active)
if st.session_state.topic and st.session_state.page != "home":
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:1rem;">
            <div style="font-size:0.75rem; color:#4a5568; text-transform:uppercase; letter-spacing:2px;">Learning</div>
            <div style="font-size:1.1rem; font-weight:700; color:#00d4ff; margin-top:0.3rem;">{st.session_state.topic}</div>
            <div style="font-size:0.8rem; color:#8892a4;">{st.session_state.level} · {st.session_state.language}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("🏠", "Home", "home"),
            ("📊", "Dashboard", "dashboard"),
            ("📖", "Lesson", "lesson"),
            ("🧪", "Quiz", "quiz"),
            ("🏆", "Certifications", "certification"),
            ("─────────────", "", ""),
            ("🤖", "AI Doubt Solver", "doubt_solver"),
            ("💪", "Practice Problems", "practice"),
            ("🃏", "Flashcards", "flashcards"),
            ("🎤", "Mock Interview", "interview"),
            ("📅", "Study Plan", "study_plan"),
            ("📄", "Cheat Sheet", "cheat_sheet"),
        ]

        for icon, label, page_key in nav_items:
            if page_key == "":
                st.markdown(f'<div style="color:#2d3748; font-size:0.7rem; padding:0.3rem 0;">{icon}</div>', unsafe_allow_html=True)
                continue
            is_active = st.session_state.page == page_key
            bg = "rgba(0,212,255,0.15)" if is_active else "transparent"
            color = "#00d4ff" if is_active else "#8892a4"
            border = "1px solid rgba(0,212,255,0.3)" if is_active else "1px solid transparent"
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

# Route to correct page
page = st.session_state.page
if page == "home":
    show_home()
elif page == "lesson":
    show_lesson()
elif page == "quiz":
    show_quiz()
elif page == "certification":
    show_certification()
elif page == "doubt_solver":
    show_doubt_solver()
elif page == "practice":
    show_practice()
elif page == "flashcards":
    show_flashcards()
elif page == "study_plan":
    show_study_plan()
elif page == "interview":
    show_interview()
elif page == "cheat_sheet":
    show_cheat_sheet()
elif page == "dashboard":
    show_dashboard()
