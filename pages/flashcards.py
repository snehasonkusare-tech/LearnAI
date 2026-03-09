import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import generate_flashcards
import streamlit.components.v1 as components

def show_flashcards():
    topic = st.session_state.get("topic", "")

    # Init hard/easy tracking
    if "flashcard_mastered" not in st.session_state:
        st.session_state.flashcard_mastered = set()
    if "flashcard_review" not in st.session_state:
        st.session_state.flashcard_review = set()

    mastered = len(st.session_state.flashcard_mastered)
    needs_review = len(st.session_state.flashcard_review)
    if mastered > 0 or needs_review > 0:
        st.markdown(f"""
        <div style="display:flex; gap:1rem; margin-bottom:1rem;">
            <div style="padding:0.5rem 1rem; background:rgba(0,255,136,0.1);
                        border:1px solid rgba(0,255,136,0.3); border-radius:8px;
                        color:#00ff88; font-size:0.85rem;">👍 Mastered: {mastered}</div>
            <div style="padding:0.5rem 1rem; background:rgba(255,107,107,0.1);
                        border:1px solid rgba(255,107,107,0.3); border-radius:8px;
                        color:#ff6b6b; font-size:0.85rem;">👎 Review: {needs_review}</div>
        </div>
        """, unsafe_allow_html=True)
    level = st.session_state.get("level", "Beginner")
    language = st.session_state.get("language", "English")
    lesson_data = st.session_state.get("lesson_data")

    if st.button("← Back to Lesson"):
        st.session_state.page = "lesson"
        st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Flashcards</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div class="hero-title" style="font-size:2.2rem;">🃏 Flashcard Mode</div>
        <div class="hero-subtitle">Flip cards to test your memory — quick revision made easy</div>
    </div>
    """, unsafe_allow_html=True)

    chapters = lesson_data.get("chapters", []) if lesson_data else []
    chapter_names = [f"Chapter {c['number']}: {c['title']}" for c in chapters]

    if not chapter_names:
        st.warning("Please complete at least one chapter first.")
        return

    selected = st.selectbox("Choose a chapter", chapter_names)
    chapter_title = selected.split(": ", 1)[1] if ": " in selected else topic
    cache_key = f"flashcards_{chapter_title}"

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 New Cards"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()

    if cache_key not in st.session_state:
        with st.spinner(f"🃏 Generating flashcards for {chapter_title}..."):
            cards = generate_flashcards(topic, chapter_title, level, language)
            st.session_state[cache_key] = cards

    cards = st.session_state[cache_key]
    if not cards:
        st.error("Could not generate flashcards. Try again.")
        return

    # Render interactive flashcard widget
    cards_json = str(cards).replace("'", '"').replace('True', 'true').replace('False', 'false')

    html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: transparent; font-family: 'Space Grotesk', sans-serif; }}

        .fc-container {{ max-width: 700px; margin: 0 auto; padding: 1rem; }}

        .fc-counter {{
            text-align: center;
            color: #00d4ff;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 1.5rem;
        }}

        .fc-card-wrapper {{
            perspective: 1000px;
            height: 260px;
            margin-bottom: 1.5rem;
            cursor: pointer;
        }}

        .fc-card {{
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.6s ease;
            border-radius: 16px;
        }}

        .fc-card.flipped {{ transform: rotateY(180deg); }}

        .fc-front, .fc-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            text-align: center;
        }}

        .fc-front {{
            background: linear-gradient(135deg, rgba(0,212,255,0.12), rgba(123,97,255,0.12));
            border: 1px solid rgba(0,212,255,0.3);
        }}

        .fc-back {{
            background: linear-gradient(135deg, rgba(0,255,136,0.08), rgba(123,97,255,0.08));
            border: 1px solid rgba(0,255,136,0.3);
            transform: rotateY(180deg);
        }}

        .fc-label {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 1rem;
        }}
        .fc-front .fc-label {{ color: #00d4ff; }}
        .fc-back .fc-label {{ color: #00ff88; }}

        .fc-text {{
            font-size: 1.1rem;
            color: #ffffff;
            font-weight: 600;
            line-height: 1.6;
        }}
        .fc-back .fc-text {{
            font-size: 0.95rem;
            font-weight: 400;
            color: #c9d3e0;
        }}

        .fc-hint {{
            font-size: 0.8rem;
            color: #4a5568;
            margin-top: 1rem;
        }}

        .fc-nav {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            align-items: center;
            margin-bottom: 1.5rem;
        }}

        .fc-btn {{
            background: linear-gradient(135deg, #00d4ff, #7b61ff);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 700;
            font-size: 0.9rem;
            padding: 0.6rem 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .fc-btn:hover {{ transform: translateY(-2px); opacity: 0.9; }}
        .fc-btn:disabled {{ opacity: 0.4; cursor: default; transform: none; }}

        .fc-flip-btn {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px;
            color: #c9d3e0;
            font-size: 0.9rem;
            padding: 0.6rem 1.5rem;
            cursor: pointer;
        }}

        .fc-progress {{
            display: flex;
            gap: 6px;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .fc-dot {{
            width: 10px; height: 10px;
            border-radius: 50%;
            background: rgba(255,255,255,0.15);
            transition: background 0.3s;
        }}
        .fc-dot.active {{ background: #00d4ff; }}
        .fc-dot.seen {{ background: rgba(0,212,255,0.4); }}

        .fc-score {{
            text-align:center;
            color: #8892a4;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }}
    </style>

    <div class="fc-container">
        <div class="fc-counter" id="counter">Card 1 of {len(cards)}</div>

        <div class="fc-card-wrapper" onclick="flipCard()">
            <div class="fc-card" id="card">
                <div class="fc-front">
                    <div class="fc-label">❓ Question</div>
                    <div class="fc-text" id="front-text"></div>
                    <div class="fc-hint">Click to reveal answer</div>
                </div>
                <div class="fc-back">
                    <div class="fc-label">✅ Answer</div>
                    <div class="fc-text" id="back-text"></div>
                </div>
            </div>
        </div>

        <div class="fc-nav">
            <button class="fc-btn" onclick="prevCard()" id="prevBtn" disabled>← Prev</button>
            <button class="fc-flip-btn" onclick="flipCard()">🔄 Flip</button>
            <button class="fc-btn" onclick="nextCard()" id="nextBtn">Next →</button>
        </div>

        <div class="fc-progress" id="progress"></div>
        <div class="fc-score" id="scoreText"></div>
    </div>

    <script>
        const cards = {cards_json};
        let current = 0;
        let seen = new Set();
        let isFlipped = false;

        function renderCard() {{
            const card = cards[current];
            document.getElementById('front-text').innerText = card.front || card['front'];
            document.getElementById('back-text').innerText = card.back || card['back'];
            document.getElementById('counter').innerText = `Card ${{current + 1}} of ${{cards.length}}`;
            document.getElementById('prevBtn').disabled = current === 0;
            document.getElementById('nextBtn').disabled = current === cards.length - 1;
            document.getElementById('card').classList.remove('flipped');
            isFlipped = false;
            renderDots();
        }}

        function renderDots() {{
            const prog = document.getElementById('progress');
            prog.innerHTML = '';
            cards.forEach((_, i) => {{
                const dot = document.createElement('div');
                dot.className = 'fc-dot' + (i === current ? ' active' : seen.has(i) ? ' seen' : '');
                prog.appendChild(dot);
            }});
            document.getElementById('scoreText').innerText = seen.size > 0 ? `${{seen.size}} of ${{cards.length}} cards reviewed` : '';
        }}

        function flipCard() {{
            isFlipped = !isFlipped;
            document.getElementById('card').classList.toggle('flipped', isFlipped);
            if (isFlipped) seen.add(current);
            renderDots();
        }}

        function nextCard() {{
            if (current < cards.length - 1) {{
                current++;
                renderCard();
            }}
        }}

        function prevCard() {{
            if (current > 0) {{
                current--;
                renderCard();
            }}
        }}

        renderCard();
    </script>
    """

    components.html(html, height=500)

    st.markdown(f"""
    <div style="text-align:center; color:#4a5568; font-size:0.85rem; margin-top:1rem;">
        📖 {len(cards)} flashcards generated for <span style="color:#00d4ff;">{chapter_title}</span>
    </div>
    """, unsafe_allow_html=True)
