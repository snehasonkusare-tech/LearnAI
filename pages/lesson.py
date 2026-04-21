import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_utils import generate_lesson_structure, generate_chapter_content, generate_flow_diagram
from components.video_player import show_video_player
import urllib.parse

def make_youtube_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

def show_lesson():
    topic = st.session_state.topic
    level = st.session_state.level
    language = st.session_state.language

    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown(f'<div class="nav-breadcrumb">Home → <span>{topic}</span> → Lesson</div>', unsafe_allow_html=True)

    # Feature toolbar (only when reading a chapter)
    if st.session_state.current_chapter > 0:
        st.markdown("""
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:1.5rem;">
            <span style="color:#4a5568; font-size:0.8rem; padding-top:0.4rem;">Quick access:</span>
        </div>
        """, unsafe_allow_html=True)
        tc1, tc2, tc3, tc4, tc5, tc6 = st.columns(6)
        with tc1:
            if st.button("🤖 Ask AI", key="tb_doubt"):
                st.session_state.page = "doubt_solver"
                st.rerun()
        with tc2:
            if st.button("💪 Practice", key="tb_practice"):
                st.session_state.page = "practice"
                st.rerun()
        with tc3:
            if st.button("🃏 Flashcards", key="tb_flash"):
                st.session_state.page = "flashcards"
                st.rerun()
        with tc4:
            if st.button("🎤 Interview", key="tb_interview"):
                st.session_state.page = "interview"
                st.rerun()
        with tc5:
            if st.button("📅 Study Plan", key="tb_plan"):
                st.session_state.page = "study_plan"
                st.rerun()
        with tc6:
            if st.button("📄 Cheat Sheet", key="tb_cheat"):
                st.session_state.page = "cheat_sheet"
                st.rerun()
        st.markdown("---")

    if st.session_state.lesson_data is None:
        with st.spinner(f"🧠 Building your personalized lesson on **{topic}**..."):
            try:
                lesson_data = generate_lesson_structure(topic, level, language)
                if lesson_data:
                    st.session_state.lesson_data = lesson_data
                else:
                    # Show raw response for debugging
                    st.error("⚠️ Could not parse lesson structure. Trying simplified generation...")
                    # Fallback: build lesson manually without AI structure call
                    lesson_data = build_fallback_structure(topic, level, language)
                    st.session_state.lesson_data = lesson_data
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Trying fallback mode...")
                lesson_data = build_fallback_structure(topic, level, language)
                st.session_state.lesson_data = lesson_data

    lesson_data = st.session_state.lesson_data
    if not lesson_data:
        st.error("Could not generate lesson. Please go back and try again.")
        return

    chapters = lesson_data.get("chapters", [])
    total_chapters = len(chapters)

    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">{lesson_data.get('topic', topic)}</div>
        <div class="hero-subtitle">{lesson_data.get('tagline', f'Master {topic} step by step')}</div>
        <div style="display: flex; gap: 0.8rem; flex-wrap: wrap;">
            <span class="section-label label-explanation">📚 {level}</span>
            <span class="section-label label-analogy">🌍 {language}</span>
            <span class="section-label label-example">📖 {total_chapters} Chapters</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Syllabus view
    if st.session_state.current_chapter == 0:
        st.markdown('<div class="card-title" style="font-size:1.6rem; margin-bottom:1.5rem;">📋 Your Lesson Plan</div>', unsafe_allow_html=True)

        for i, chapter in enumerate(chapters):
            col_ch, col_btn = st.columns([4, 1])
            with col_ch:
                st.markdown(f"""
                <div class="chapter-card">
                    <div class="chapter-number">Chapter {chapter['number']}</div>
                    <div class="chapter-title">{chapter['title']}</div>
                    <div class="card-text" style="font-size:0.9rem; margin-top:0.3rem;">{chapter.get('description','')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button(f"Start →", key=f"start_ch_{i}"):
                    st.session_state.current_chapter = i + 1
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Start From Chapter 1", key="start_all"):
            st.session_state.current_chapter = 1
            st.rerun()

    else:
        chapter_idx = st.session_state.current_chapter - 1
        chapter = chapters[chapter_idx]

        # Progress bar
        progress = st.session_state.current_chapter / total_chapters
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                <span style="color:#8892a4; font-size:0.85rem;">Chapter {st.session_state.current_chapter} of {total_chapters}</span>
                <span style="color:#00d4ff; font-size:0.85rem; font-weight:600;">{int(progress*100)}% Complete</span>
            </div>
            <div class="progress-container">
                <div style="height:6px; width:{int(progress*100)}%; background: linear-gradient(90deg, #00d4ff, #7b61ff); border-radius:10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <div class="chapter-number">Chapter {chapter['number']} of {total_chapters}</div>
            <div class="hero-title" style="font-size:2rem;">{chapter['title']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Top nav buttons — no more scrolling to bottom
        top_prev, top_mid, top_next = st.columns([1, 2, 1])
        with top_prev:
            if st.session_state.current_chapter > 1:
                if st.button("← Prev", key="top_prev_btn"):
                    st.session_state.current_chapter -= 1
                    st.rerun()
        with top_mid:
            st.markdown(f'<div style="text-align:center; color:#4a5568; font-size:0.85rem; padding-top:0.5rem;">{st.session_state.current_chapter} / {total_chapters}</div>', unsafe_allow_html=True)
        with top_next:
            if st.session_state.current_chapter < total_chapters:
                if st.button("Next →", key="top_next_btn"):
                    if "completed_chapters" not in st.session_state:
                        st.session_state.completed_chapters = set()
                    st.session_state.completed_chapters.add(chapter_idx)
                    st.session_state.current_chapter += 1
                    st.rerun()
        st.markdown("---")

        # Generate content
        cache_key = f"chapter_content_{chapter_idx}"
        if cache_key not in st.session_state:
            with st.spinner(f"✍️ Writing detailed lesson for **{chapter['title']}**..."):
                try:
                    content = generate_chapter_content(topic, chapter['title'], chapter['number'], level, language)
                    if content:
                        st.session_state[cache_key] = content
                    else:
                        st.warning("Using simplified content for this chapter.")
                        st.session_state[cache_key] = build_fallback_chapter(topic, chapter['title'])
                except Exception as e:
                    st.warning(f"Note: {str(e)[:100]}. Using fallback content.")
                    st.session_state[cache_key] = build_fallback_chapter(topic, chapter['title'])

        content = st.session_state[cache_key]

        # Generate chapter-specific flow diagram (cached)
        flow_key = f"chapter_flow_{chapter_idx}"
        if flow_key not in st.session_state:
            try:
                flow_data = generate_flow_diagram(topic, chapter['title'], level, language)
                st.session_state[flow_key] = flow_data
            except Exception:
                st.session_state[flow_key] = {}
        content = dict(content)  # make a copy so we don't mutate cached content
        content['flow_diagram'] = st.session_state.get(flow_key, {})

        # 1. Full Explanation
        st.markdown('<span class="section-label label-explanation">📖 Full Explanation</span>', unsafe_allow_html=True)
        explanation = content.get("explanation", "")
        # Split into paragraphs for better readability
        paragraphs = [p.strip() for p in explanation.split('\n') if p.strip()]
        para_html = "".join([f'<p style="margin-bottom:1rem; color:#c9d3e0; line-height:1.9; font-size:1.05rem;">{p}</p>' for p in paragraphs])
        st.markdown(f'<div class="card">{para_html}</div>', unsafe_allow_html=True)

        # VIDEO PLAYER
        st.markdown('<span class="section-label label-visual">🎬 AI Video Explanation</span>', unsafe_allow_html=True)
        show_video_player(content, chapter['title'], topic)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Key Concepts
        # 2. Key Concepts
        key_concepts = content.get("key_concepts", [])
        if key_concepts:
            st.markdown('<span class="section-label label-example">🔑 Key Concepts</span>', unsafe_allow_html=True)
            cols = st.columns(2)
            for i, concept in enumerate(key_concepts):
                with cols[i % 2]:
                    if ": " in concept:
                        cname, cdesc = concept.split(": ", 1)
                    else:
                        cname, cdesc = f"Concept {i+1}", concept

                    # Strip ** * __ _ markdown formatting from title and description
                    cname = cname.strip().strip("*").strip("_").strip("*").strip()
                    cdesc = cdesc.strip().strip("*").strip("_").strip("*").strip()
                    import re as _re
                    cname = _re.sub(r'\*{1,2}|_{1,2}', '', cname).strip()
                    cdesc = _re.sub(r'\*{1,2}|_{1,2}', '', cdesc).strip()

                    st.markdown(f"""
                    <div style="background:rgba(123,97,255,0.08); border:1px solid rgba(123,97,255,0.2);
                                border-radius:10px; padding:1rem; margin-bottom:0.8rem;">
                        <div style="color:#a78bfa; font-size:0.85rem; font-weight:700; margin-bottom:0.4rem;">{cname}</div>
                        <div style="color:#c9d3e0; font-size:0.9rem; line-height:1.7;">{cdesc}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 3. Real Life Analogy
        st.markdown('<span class="section-label label-analogy">🌍 Real Life Analogy</span>', unsafe_allow_html=True)
        analogy_paras = [p.strip() for p in content.get("analogy","").split('\n') if p.strip()]
        analogy_html = "".join([f'<p style="margin-bottom:0.8rem; color:#c9d3e0; line-height:1.9;">💬 {p}</p>' for p in analogy_paras])
        st.markdown(f'<div class="card">{analogy_html}</div>', unsafe_allow_html=True)

        # 4. Step-by-Step Example
        st.markdown('<span class="section-label label-example">💡 Step-by-Step Example</span>', unsafe_allow_html=True)
        example_lines = content.get("example","").split("\n")
        example_html = ""
        for line in example_lines:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("step"):
                parts = line.split(":", 1)
                step_label = parts[0].strip()
                step_content = parts[1].strip() if len(parts) > 1 else ""
                is_code = any(p in step_content for p in [
                    "()", "[]", "{}", "import ", "def ", "class ",
                    "$ ", "npm ", "pip ", "git ", "docker ", "->", "=>"
                ])
                if is_code:
                    # Flush any buffered html first
                    if example_html:
                        st.markdown(f'<div class="card">{example_html}</div>', unsafe_allow_html=True)
                        example_html = ""
                    st.markdown(f'<div style="color:#7b61ff; font-weight:700; font-size:0.85rem; margin-bottom:0.3rem;">{step_label}</div>', unsafe_allow_html=True)
                    st.code(step_content)
                else:
                    example_html += f"""
                    <div style="display:flex; gap:1rem; margin-bottom:1rem; padding:1rem;
                                background:rgba(255,255,255,0.02); border-radius:10px;
                                border-left:3px solid #7b61ff;">
                        <div style="color:#7b61ff; font-weight:700; font-size:0.85rem;
                                    min-width:70px; padding-top:0.1rem;">{step_label}</div>
                        <div style="color:#c9d3e0; line-height:1.8; font-size:0.95rem;">{step_content}</div>
                    </div>"""
            else:
                example_html += f'<p style="color:#c9d3e0; line-height:1.8; margin-bottom:0.5rem;">{line}</p>'
        st.markdown(f'<div class="card">{example_html}</div>', unsafe_allow_html=True)

        # 5. Visual Diagram
        st.markdown('<span class="section-label label-visual">🎨 Visual Diagram</span>', unsafe_allow_html=True)
        visual = content.get("visual", "")
        st.markdown(f'<div style="overflow-x:auto; background:#0a0a1e; padding:1rem; border-radius:10px; font-family:monospace; font-size:0.85rem; line-height:1.7; white-space:pre;">{visual}</div>', unsafe_allow_html=True)

        # 6. Common Mistakes
        common_mistakes = content.get("common_mistakes", "")
        if common_mistakes:
            st.markdown('<span class="section-label" style="background:rgba(255,107,107,0.15);color:#ff6b6b;border:1px solid rgba(255,107,107,0.3);">⚠️ Common Mistakes to Avoid</span>', unsafe_allow_html=True)
            mistake_paras = [p.strip() for p in common_mistakes.split('\n') if p.strip()]
            mistake_html = "".join([f'<p style="margin-bottom:1rem; color:#c9d3e0; line-height:1.8;">{p}</p>' for p in mistake_paras])
            st.markdown(f'<div class="card" style="border-color:rgba(255,107,107,0.2);">{mistake_html}</div>', unsafe_allow_html=True)

        # 7. YouTube Video Links
        youtube_searches = content.get("youtube_searches", [])
        if youtube_searches:
            st.markdown('<span class="section-label label-visual">🎬 Watch & Learn — Video Tutorials</span>', unsafe_allow_html=True)
            st.markdown('<div class="card"><div style="color:#8892a4; font-size:0.9rem; margin-bottom:1rem;">Click to find video tutorials on YouTube for this chapter:</div>', unsafe_allow_html=True)
            icons = ["🎯", "📺", "🔍"]
            labels = ["Beginner Tutorial", "Visual Explanation", "Deep Dive"]
            for i, search_query in enumerate(youtube_searches):
                url = make_youtube_url(search_query)
                st.markdown(f"""
                <a href="{url}" target="_blank" style="display:block; padding:0.9rem 1.2rem;
                   background:rgba(255,0,0,0.08); border:1px solid rgba(255,0,0,0.2);
                   border-radius:10px; margin-bottom:0.7rem; text-decoration:none;">
                    <span style="color:#ff4444; font-weight:700; font-size:0.85rem;">
                        {icons[i] if i < len(icons) else '▶️'} {labels[i] if i < len(labels) else 'Video'} →
                    </span>
                    <span style="color:#c9d3e0; font-size:0.9rem; margin-left:0.5rem;">"{search_query}"</span>
                </a>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 8. Key Takeaway
        st.markdown("<br>", unsafe_allow_html=True)
        takeaway_paras = [p.strip() for p in content.get("key_takeaway","").split('\n') if p.strip()]
        takeaway_html = "".join([f'<p style="color:white; font-size:1.05rem; line-height:1.8; margin-bottom:0.6rem;">{p}</p>' for p in takeaway_paras])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(123,97,255,0.1));
                    border: 1px solid rgba(0,212,255,0.3); border-radius: 12px; padding: 1.5rem;
                    margin-bottom: 2rem;">
            <div style="color:#00d4ff; font-weight:600; font-size:0.8rem; text-transform:uppercase;
                        letter-spacing:2px; margin-bottom:0.8rem;">⭐ Key Takeaway</div>
            {takeaway_html}
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        col_prev, col_mid, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.session_state.current_chapter > 1:
                if st.button("← Previous"):
                    st.session_state.current_chapter -= 1
                    st.rerun()
            else:
                if st.button("📋 Syllabus"):
                    st.session_state.current_chapter = 0
                    st.rerun()

        with col_mid:
            st.markdown(f'<div style="text-align:center; color:#4a5568; font-size:0.9rem; padding-top:0.6rem;">{st.session_state.current_chapter} / {total_chapters}</div>', unsafe_allow_html=True)

        with col_next:
            if st.session_state.current_chapter < total_chapters:
                if st.button("Next Chapter →"):
                    st.session_state.current_chapter += 1
                    st.rerun()
            else:
                if st.button("🧪 Take Quiz →"):
                    st.session_state.page = "quiz"
                    st.rerun()


def build_fallback_structure(topic: str, level: str, language: str) -> dict:
    """Build a lesson structure without needing AI JSON parsing."""
    from utils.ai_utils import call_groq
    try:
        # Ask for plain text chapters, then parse manually
        response = call_groq(
            "You are a curriculum designer. List chapter titles only, one per line, no numbering, no JSON.",
            f"List 6 chapter titles for learning '{topic}' at {level} level in {language}. One title per line only."
        )
        lines = [l.strip() for l in response.strip().split('\n') if l.strip()][:6]
        chapters = [{"number": i+1, "title": line, "description": f"Learn about {line} in depth."} for i, line in enumerate(lines)]
    except Exception:
        chapters = [
            {"number": 1, "title": f"Introduction to {topic}", "description": f"What is {topic} and why does it matter?"},
            {"number": 2, "title": f"Core Concepts of {topic}", "description": "The fundamental building blocks."},
            {"number": 3, "title": f"How {topic} Works", "description": "Step by step breakdown of the mechanism."},
            {"number": 4, "title": f"Practical Examples", "description": "Real world use cases and applications."},
            {"number": 5, "title": f"Common Patterns in {topic}", "description": "Patterns and best practices."},
            {"number": 6, "title": f"Next Steps with {topic}", "description": "Where to go from here."},
        ]
    return {
        "topic": topic,
        "tagline": f"Master {topic} from beginner to confident practitioner.",
        "total_chapters": len(chapters),
        "chapters": chapters
    }


def build_fallback_chapter(topic: str, chapter_title: str) -> dict:
    """Fallback chapter content if AI fails."""
    return {
        "explanation": f"In this chapter we explore {chapter_title} as part of learning {topic}. This is a fundamental concept that builds your understanding. Take your time going through this material and make sure each idea clicks before moving forward.",
        "analogy": f"Think of {chapter_title} like learning the rules of a board game. Before you can play well, you need to understand what each piece does and why the rules exist. Once those rules make sense, you start seeing strategies everywhere.",
        "example": "Step 1 - Understand the goal: Know what you are trying to achieve.\nStep 2 - Break it down: Divide the problem into smaller parts.\nStep 3 - Start simple: Begin with the most basic version.\nStep 4 - Test it: Check if it works as expected.\nStep 5 - Improve: Refine based on what you learned.",
        "visual": f"""
+---------------------------+
|    {chapter_title[:25]}    |
+---------------------------+
           |
           v
  +--------+--------+
  |                 |
  v                 v
[Concept A]    [Concept B]
  |                 |
  v                 v
  +--------+--------+
           |
           v
    [Final Result]
        """,
        "key_concepts": [
            f"Core Idea: The main concept of {chapter_title} explained simply.",
            f"How It Works: The mechanism behind {chapter_title}.",
            f"Why It Matters: The importance of {chapter_title} in {topic}.",
            f"Application: How {chapter_title} is used in real projects."
        ],
        "common_mistakes": f"Mistake 1: Skipping basics and jumping ahead too fast.\nMistake 2: Memorizing without understanding the why.\nMistake 3: Not practicing with real examples.",
        "key_takeaway": f"{chapter_title} is a core building block of {topic}. Understanding it well will make every following chapter easier and more intuitive.",
        "youtube_searches": [
            f"{topic} {chapter_title} tutorial for beginners",
            f"{chapter_title} explained simply {topic}",
            f"how {chapter_title} works {topic} visual"
        ]
    }
