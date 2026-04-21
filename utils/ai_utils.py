import json
import re
import os
import time
import streamlit as st
from groq import Groq

def get_client():
    api_key = None
    possible_keys = ["GROQ_API_KEY", "groq_api_key", "groq_API_KEY", "Groq_API_Key", "GROQ_api_key"]
    for key in possible_keys:
        try:
            val = st.secrets.get(key)
            if val:
                api_key = val
                break
        except Exception:
            pass
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("API key not found. Open `.streamlit/secrets.toml` and paste:\nGROQ_API_KEY = \"gsk_your_key_here\"")
        st.stop()
    return Groq(api_key=api_key)

def call_groq(system_prompt: str, user_prompt: str, max_tokens: int = 4000) -> str:
    client = get_client()

    # Try primary model first, fallback to faster model on rate limit
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]

    for attempt, model in enumerate(models):
        try:
            if attempt > 0:
                time.sleep(2)  # small wait before fallback
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            err = str(e)
            if "429" in err or "rate limit" in err.lower():
                if attempt < len(models) - 1:
                    time.sleep(3)  # wait 3 seconds before trying next model
                    continue
            raise e

    raise Exception("All models rate limited. Please wait a moment and try again.")

def parse_json_response(text: str):
    if not text:
        return None
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    try:
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    try:
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass
    return None

def get_chapter_count(topic: str) -> int:
    very_complex = ["machine learning", "deep learning", "artificial intelligence",
                    "data science", "cybersecurity", "cloud computing", "devops",
                    "python", "javascript", "full stack", "software engineering"]
    moderately_complex = ["neural network", "blockchain", "kubernetes", "docker", "react",
                          "nlp", "natural language processing", "computer vision", "aws",
                          "django", "fastapi", "tensorflow", "pytorch", "sql", "databases",
                          "api", "microservices", "git", "linux", "networking"]
    medium_topics = ["html", "css", "node", "vue", "angular", "flask", "pandas",
                     "numpy", "matplotlib", "power bi", "tableau", "excel", "spark",
                     "hadoop", "kafka", "redis", "mongodb", "postgresql"]
    topic_lower = topic.lower()
    for t in very_complex:
        if t in topic_lower:
            return 12
    for t in moderately_complex:
        if t in topic_lower:
            return 10
    for t in medium_topics:
        if t in topic_lower:
            return 8
    try:
        response = call_groq(
            "You are a curriculum expert. Answer with a single number only. No text.",
            f"How many chapters would a complete, thorough course on '{topic}' need? Answer with just a number between 6 and 12."
        )
        num = int(''.join(filter(str.isdigit, response.strip()[:3])))
        if 6 <= num <= 12:
            return num
    except Exception:
        pass
    return 7

def generate_lesson_structure(topic: str, level: str, language: str) -> dict:
    num_chapters = get_chapter_count(topic)

    level_instructions = {
        "Beginner": f"Assume the student knows NOTHING about {topic}. Start from absolute zero. Chapters must go from 'What is {topic}?' to basic practical usage. Use simple words. No advanced concepts.",
        "Intermediate": f"Assume the student already knows the basics of {topic}. DO NOT include introductory chapters. Focus on how things work internally, common patterns, real-world projects, debugging, and practical skills.",
        "Advanced": f"Assume the student is already comfortable using {topic}. Focus entirely on deep internals, system design, optimization, edge cases, production-level knowledge, architecture, and expert-level mastery."
    }
    level_guide = level_instructions.get(level, level_instructions["Beginner"])

    chapters_list = "\n".join([
        f'    {{"number": {i}, "title": "specific {level}-level chapter {i} title about {topic} in {language}", "description": "2 sentences about this {level}-level chapter on {topic} in {language}"}}{","  if i < num_chapters else ""}'
        for i in range(1, num_chapters + 1)
    ])

    system = """You are an expert curriculum designer. Respond with valid JSON only.
No markdown, no extra text. Start with { and end with }."""

    user = f"""Create a lesson plan for: "{topic}" at {level} level in {language}.

CRITICAL LEVEL INSTRUCTION: {level_guide}

Chapters must be COMPLETELY DIFFERENT based on level:
- Beginner chapters: "What is {topic}?", "Setting up {topic}", "Basic {topic} concepts"
- Intermediate chapters: "How {topic} works internally", "Common {topic} patterns", "Building real {topic} projects"  
- Advanced chapters: "{topic} Architecture", "{topic} Optimization", "Production {topic} best practices"

Current level is {level} — write ONLY {level}-appropriate chapters. Make {num_chapters} total.

Return ONLY this JSON:
{{
  "topic": "{topic}",
  "tagline": "compelling sentence about mastering {topic} at {level} level",
  "total_chapters": {num_chapters},
  "chapters": [
{chapters_list}
  ]
}}"""

    response = call_groq(system, user, max_tokens=2000)
    result = parse_json_response(response)
    if not result:
        result = build_structure_from_text(topic, level, language, num_chapters)
    return result


def build_structure_from_text(topic: str, level: str, language: str, num_chapters: int) -> dict:
    level_prompt = {
        "Beginner": f"Start from scratch. First chapter must be 'What is {topic}?'. Build up from zero knowledge.",
        "Intermediate": f"Skip basics. Focus on how {topic} works internally, patterns, and real projects.",
        "Advanced": f"Focus on {topic} internals, optimization, architecture, production, and expert techniques."
    }.get(level, "")

    try:
        response = call_groq(
            f"You are a curriculum designer for {topic}. List exactly {num_chapters} specific {level}-level chapter titles. One per line. No numbers, no JSON.",
            f"List {num_chapters} {level}-level chapter titles for {topic} in {language}. {level_prompt} One per line only."
        )
        lines = [l.strip().lstrip('0123456789.-) ') for l in response.strip().split('\n') if l.strip()]
        lines = [l for l in lines if len(l) > 3][:num_chapters]
        chapters = [{"number": i+1, "title": line,
                     "description": f"This {level}-level chapter covers {line} — a key part of {topic} for {level} learners."}
                    for i, line in enumerate(lines)]
        while len(chapters) < num_chapters:
            n = len(chapters) + 1
            chapters.append({"number": n, "title": f"{topic} {level} - Part {n}",
                              "description": f"Advanced {topic} concepts for {level} level learners."})
        return {"topic": topic, "tagline": f"Master {topic} at {level} level — step by step.",
                "total_chapters": len(chapters), "chapters": chapters}
    except Exception:
        return None


def generate_chapter_content(topic: str, chapter_title: str, chapter_number: int, level: str, language: str) -> dict:

    level_depth = {
        "Beginner": f"Use simple words. Explain every term. Assume zero prior knowledge of {topic}.",
        "Intermediate": f"Assume basic {topic} knowledge. Use proper terminology. Include practical patterns.",
        "Advanced": f"Assume strong foundation. Cover internals, edge cases, architecture. Use expert terminology."
    }
    depth_guide = level_depth.get(level, level_depth["Beginner"])

    time.sleep(1)

    # SINGLE CALL — get everything at once in plain text with clear separators
    full_content = call_groq(
        f"You are a world-class expert and teacher in {topic}. Write like you are personally teaching a {level} student. Every sentence must be specific to '{chapter_title}' in {topic}. Never write generic content.",
        f"""Write a complete lesson for "{chapter_title}" in {topic} at {level} level in {language}.
DEPTH: {depth_guide}

Use EXACTLY these section headers and write content under each:

##EXPLANATION##
Write 6-8 paragraphs specifically about "{chapter_title}" in {topic}. Use real {topic} terminology. Match {level} depth.

##ANALOGY##
Write 3-4 sentences with a real-life analogy mapping SPECIFICALLY to "{chapter_title}" in {topic}. Map each part of analogy to a real part of {chapter_title}.

##EXAMPLE##
Write 6 steps showing how "{chapter_title}" works in {topic}. Format: Step N - [specific {topic} term]: [2 sentence explanation]

##CONCEPTS##
Write exactly 4 key concepts. Format each as:
CONCEPT: [specific {topic} term]
EXPLANATION: [2 sentences for {level} level]

##MISTAKES##
Write 3 specific mistakes {level} learners make with "{chapter_title}" in {topic}. Each must be specific to {topic}.

##VISUAL##
ASCII diagram of "{chapter_title}" in {topic}. Use real {topic} labels. At least 12 lines. No explanation text.

##TAKEAWAY##
Write 2-3 sentences summarizing what was learned about "{chapter_title}" in {topic} at {level} level.

Write in {language}. Be specific to {topic} throughout.""",
        max_tokens=4000
    )

    # Parse sections
    sections = {}
    current_section = None
    current_lines = []

    for line in full_content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('##') and stripped.endswith('##'):
            if current_section and current_lines:
                sections[current_section] = '\n'.join(current_lines).strip()
            current_section = stripped.strip('#').strip()
            current_lines = []
        elif current_section:
            current_lines.append(line)

    if current_section and current_lines:
        sections[current_section] = '\n'.join(current_lines).strip()

    # Parse key concepts from CONCEPTS section
    key_concepts = []
    concepts_text = sections.get('CONCEPTS', '')
    current_concept = ""
    current_explanation = ""
    for line in concepts_text.split('\n'):
        line = line.strip()
        if line.upper().startswith('CONCEPT:'):
            if current_concept and current_explanation:
                key_concepts.append(f"{current_concept}: {current_explanation}")
            current_concept = line.split(':', 1)[1].strip()
            current_explanation = ""
        elif line.upper().startswith('EXPLANATION:'):
            current_explanation = line.split(':', 1)[1].strip()
        elif current_explanation and line:
            current_explanation += " " + line
    if current_concept and current_explanation:
        key_concepts.append(f"{current_concept}: {current_explanation}")
    if not key_concepts:
        blocks = [b.strip() for b in concepts_text.split('\n\n') if b.strip()]
        key_concepts = [b.replace('\n', ' ')[:200] for b in blocks[:4]]

    return {
        "explanation": sections.get('EXPLANATION', f"This chapter covers {chapter_title} in {topic}."),
        "analogy": sections.get('ANALOGY', f"Think of {chapter_title} like a key that unlocks deeper understanding of {topic}."),
        "example": sections.get('EXAMPLE', f"Step 1 - Understand: Learn what {chapter_title} does in {topic}.\nStep 2 - Practice: Try a simple example.\nStep 3 - Apply: Use it in a real scenario."),
        "visual": sections.get('VISUAL', f"[ {topic} ] --> [ {chapter_title} ] --> [ Result ]"),
        "key_concepts": key_concepts if key_concepts else [
            f"What {chapter_title} means in {topic}",
            f"How {chapter_title} works in {topic}",
            f"Why {chapter_title} matters for {level} learners",
            f"Where {chapter_title} is used in real {topic} projects"
        ],
        "common_mistakes": sections.get('MISTAKES', f"Not understanding the basics of {chapter_title} before applying it in {topic}."),
        "key_takeaway": sections.get('TAKEAWAY', f"{chapter_title} is a core part of {topic}. Master it and everything else becomes easier."),
        "youtube_searches": [
            f"{chapter_title} {topic} {level} tutorial explained",
            f"how {chapter_title} works {topic} visual example",
            f"{topic} {chapter_title} {level} step by step"
        ]
    }

    level_depth = {
        "Beginner": f"Use very simple words. Explain every term. Assume zero prior knowledge of {topic}. No jargon without explanation.",
        "Intermediate": f"Assume basic {topic} knowledge. Go deeper into how things work. Use proper {topic} terminology. Include practical patterns and real code concepts.",
        "Advanced": f"Assume strong {topic} foundation. Go into internals, edge cases, performance, architecture. Use expert {topic} terminology freely."
    }
    depth_guide = level_depth.get(level, level_depth["Beginner"])

    # Step 1: Deep explanation
    time.sleep(1)
    explanation = call_groq(
        f"You are a world-class expert and teacher in {topic}. Write like you are personally teaching a {level} student sitting in front of you.",
        f"""Write a detailed explanation of "{chapter_title}" as part of learning {topic} at {level} level.

DEPTH: {depth_guide}

Write 8-12 paragraphs. Every paragraph must:
- Be 100% specifically about "{chapter_title}" in {topic}
- Use real {topic} terminology, tools, and concepts
- Match {level} depth exactly
- Build naturally on the previous paragraph

Do NOT write generic content. Every sentence must mention something specific to "{chapter_title}" in {topic}.
Write in {language}. Plain text paragraphs only.""",
        max_tokens=2000
    )

    # Step 2: Real-life analogy
    analogy = call_groq(
        f"You are an expert in {topic} who explains using everyday analogies.",
        f"""Create a real-life analogy for "{chapter_title}" in {topic} at {level} level.

Pick something from daily life (cooking, sports, cities, etc).
Write 4-5 sentences. Map EACH part of the analogy to a SPECIFIC part of "{chapter_title}" in {topic}.
Make it memorable and specific. Write in {language}. Plain text only.""",
        max_tokens=500
    )

    # Step 3: Step by step example
    example = call_groq(
        f"You are an expert in {topic} who teaches through concrete {level}-level examples.",
        f"""Write a step-by-step example of "{chapter_title}" in {topic} at {level} level.

Write 6-8 steps. Format:
Step N - [Specific {topic} term]: [2-3 sentences explaining this step using real {topic} terminology]

Use a real, concrete {topic} scenario appropriate for {level} level.
Write in {language}. Plain text only.""",
        max_tokens=1000
    )

    # Step 4: Key concepts
    concepts_text = call_groq(
        f"You are an expert in {topic}.",
        f"""List 4 key {topic} concepts from "{chapter_title}" for {level} level students.

Format exactly as:
CONCEPT: [specific {topic} term]
EXPLANATION: [3 sentences explaining this {topic} term for {level} level]

Use real {topic} terminology. Write in {language}.""",
        max_tokens=800
    )

    # Parse concepts
    key_concepts = []
    lines = concepts_text.strip().split('\n')
    current_concept = ""
    current_explanation = ""
    for line in lines:
        line = line.strip()
        if line.upper().startswith("CONCEPT:"):
            if current_concept and current_explanation:
                key_concepts.append(f"{current_concept}: {current_explanation}")
            current_concept = line.split(":", 1)[1].strip() if ":" in line else line
            current_explanation = ""
        elif line.upper().startswith("EXPLANATION:"):
            current_explanation = line.split(":", 1)[1].strip() if ":" in line else line
        elif current_explanation and line:
            current_explanation += " " + line
    if current_concept and current_explanation:
        key_concepts.append(f"{current_concept}: {current_explanation}")
    if not key_concepts:
        blocks = [b.strip() for b in concepts_text.split('\n\n') if b.strip()]
        key_concepts = [b.replace('\n', ' ')[:200] for b in blocks[:4]]

    # Step 5: Common mistakes
    mistakes = call_groq(
        f"You are an expert in {topic} who has taught many {level} students.",
        f"""Write 3 common mistakes {level} learners make with "{chapter_title}" in {topic}.

For each mistake:
- Name the specific mistake (must be specific to {chapter_title} in {topic})
- Explain why {level} students make this mistake
- Explain exactly how to fix it in {topic}

Be specific to {topic} and {level} level. Write in {language}. Plain text only.""",
        max_tokens=600
    )

    # Step 6: ASCII visual diagram
    visual = call_groq(
        f"You are an expert in {topic} who creates educational ASCII diagrams.",
        f"""Create an ASCII diagram showing how "{chapter_title}" works in {topic}.

Rules:
- Label ALL boxes with real {topic} terminology from "{chapter_title}"
- Use [Box Name] for components, --> for flow, <-- for feedback
- Show the complete structure or process of "{chapter_title}" in {topic}
- At least 15 lines tall
- No explanation text — just the diagram

Plain text only.""",
        max_tokens=600
    )

    # Step 7: Key takeaway
    takeaway = call_groq(
        f"You are an expert teacher in {topic}.",
        f"""Write a key takeaway for "{chapter_title}" in {topic} at {level} level.

Write 3-4 sentences that:
- Summarize what was specifically learned about "{chapter_title}" in {topic}
- Tell the {level} student exactly what they now understand
- Connect it to what comes next in learning {topic}

Write in {language}. Plain text only.""",
        max_tokens=300
    )

    return {
        "explanation": explanation.strip(),
        "analogy": analogy.strip(),
        "example": example.strip(),
        "visual": visual.strip(),
        "key_concepts": key_concepts if key_concepts else [
            f"What {chapter_title} means in {topic} at {level} level",
            f"How {chapter_title} works inside {topic}",
            f"Why {chapter_title} matters for {level} {topic} developers",
            f"Where {chapter_title} is applied in real {topic} projects"
        ],
        "common_mistakes": mistakes.strip(),
        "key_takeaway": takeaway.strip(),
        "youtube_searches": [
            f"{chapter_title} {topic} {level} tutorial explained",
            f"how {chapter_title} works {topic} visual example",
            f"{topic} {chapter_title} {level} step by step walkthrough"
        ]
    }


def generate_quiz(topic: str, lesson_data: dict, language: str) -> dict:
    level = lesson_data.get("level", "Beginner")
    chapters_summary = "\n".join([f"- {ch['title']}" for ch in lesson_data.get("chapters", [])])
    num_questions = len(lesson_data.get("chapters", [])) + 2

    system = """You are a quiz creator. Respond with valid JSON only. No markdown. Start with { end with }."""

    user = f"""Create a {num_questions}-question quiz for "{topic}" in {language}.
Chapters: {chapters_summary}

Questions must test real understanding — not memorization.
Include scenario-based questions specific to {topic}.

Return ONLY this JSON:
{{
  "questions": [
    {{
      "question": "specific {topic} question in {language}",
      "options": ["option A", "option B", "option C", "option D"],
      "correct": 0,
      "explanation": "2-3 sentences why correct, why others wrong, in {language}"
    }}
  ]
}}
Make exactly {num_questions} questions. Vary correct index (0,1,2,3)."""

    response = call_groq(system, user, max_tokens=4000)
    return parse_json_response(response)


def generate_certification_roadmap(topic: str, level: str, language: str) -> dict:
    system = """You are a career advisor. Respond with valid JSON only. No markdown. Start with { end with }."""

    user = f"""Certification roadmap for "{topic}" at {level} level in {language}.

Return ONLY this JSON:
{{
  "certifications": [
    {{"name": "real cert name", "provider": "real provider", "level": "Beginner", "description": "3 sentences in {language}", "time_estimate": "2-3 months at 1hr/day", "cost": "$200 USD", "recommended_for": "{level}", "exam_format": "format details"}},
    {{"name": "real cert name", "provider": "real provider", "level": "Intermediate", "description": "3 sentences in {language}", "time_estimate": "3-4 months", "cost": "$300 USD", "recommended_for": "{level}", "exam_format": "format details"}},
    {{"name": "real cert name", "provider": "real provider", "level": "Advanced", "description": "3 sentences in {language}", "time_estimate": "4-6 months", "cost": "$400 USD", "recommended_for": "{level}", "exam_format": "format details"}},
    {{"name": "real cert name", "provider": "real provider", "level": "Expert", "description": "3 sentences in {language}", "time_estimate": "6+ months", "cost": "$500 USD", "recommended_for": "{level}", "exam_format": "format details"}}
  ],
  "recommended_first": "best first cert for {level}",
  "roadmap_steps": [
    "Step 1 with action and time in {language}",
    "Step 2 with action and time in {language}",
    "Step 3 with action and time in {language}",
    "Step 4 with action and time in {language}",
    "Step 5 with action and time in {language}",
    "Step 6 with action and time in {language}"
  ],
  "total_time": "realistic total time",
  "free_resources": [
    "free resource 1 name and where to find it",
    "free resource 2 name and where to find it",
    "free resource 3 name and where to find it"
  ]
}}"""

    response = call_groq(system, user, max_tokens=4000)
    return parse_json_response(response)


# ============================================================
# NEW FEATURES
# ============================================================

def ask_doubt(topic: str, chapter_title: str, level: str, language: str, question: str, chat_history: list) -> str:
    """AI Doubt Solver — answers student questions about a specific chapter."""
    history_text = ""
    for msg in chat_history[-6:]:  # last 3 exchanges
        role = "Student" if msg["role"] == "user" else "Teacher"
        history_text += f"{role}: {msg['content']}\n"

    return call_groq(
        f"You are an expert teacher in {topic} helping a {level} student understand '{chapter_title}'. "
        f"Answer clearly, specifically, and in the context of {topic}. Be friendly and encouraging. "
        f"Always relate your answer back to {chapter_title} in {topic}. Write in {language}.",
        f"""Previous conversation:
{history_text}

Student's new question: {question}

Answer specifically about "{chapter_title}" in {topic} at {level} level. 
Use real {topic} terminology. Be clear and helpful. Write in {language}.""",
        max_tokens=800
    )


def generate_practice_problems(topic: str, chapter_title: str, level: str, language: str) -> list:
    """Generate 5 fresh practice problems for a chapter."""
    response = call_groq(
        f"You are an expert {topic} problem setter creating {level}-level exercises.",
        f"""Create 5 practice problems for "{chapter_title}" in {topic} at {level} level.

For each problem write:
PROBLEM: [specific problem statement using real {topic} concepts]
HINT: [one-line hint to guide the student]
ANSWER: [clear, detailed answer/solution]

Make problems progressively harder. Be specific to {chapter_title} in {topic}.
Write in {language}. Plain text only.""",
        max_tokens=2000
    )

    problems = []
    blocks = response.strip().split('\n\n')
    current = {}
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("PROBLEM:"):
            if current.get("problem"):
                problems.append(current)
            current = {"problem": line.split(":", 1)[1].strip(), "hint": "", "answer": ""}
        elif line.upper().startswith("HINT:"):
            current["hint"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("ANSWER:"):
            current["answer"] = line.split(":", 1)[1].strip()
        elif current.get("answer") is not None and line:
            current["answer"] += " " + line
    if current.get("problem"):
        problems.append(current)

    # fallback
    if not problems:
        for i, block in enumerate(blocks[:5]):
            if len(block) > 20:
                problems.append({"problem": block[:200], "hint": f"Think about {chapter_title} concepts", "answer": "Review the chapter explanation for guidance."})

    return problems[:5]


def generate_flashcards(topic: str, chapter_title: str, level: str, language: str) -> list:
    """Generate flashcards from key concepts of a chapter."""
    response = call_groq(
        f"You are an expert in {topic} creating flashcards for {level} students.",
        f"""Create 8 flashcards for "{chapter_title}" in {topic} at {level} level.

For each flashcard:
FRONT: [question or term from {chapter_title} in {topic}]
BACK: [clear answer or definition, 2-3 sentences, specific to {topic}]

Use real {topic} terminology. Write in {language}. Plain text only.""",
        max_tokens=1500
    )

    cards = []
    current = {}
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("FRONT:"):
            if current.get("front"):
                cards.append(current)
            current = {"front": line.split(":", 1)[1].strip(), "back": ""}
        elif line.upper().startswith("BACK:"):
            current["back"] = line.split(":", 1)[1].strip()
        elif current.get("back") is not None and line and not line.upper().startswith("FRONT:"):
            current["back"] += " " + line
    if current.get("front"):
        cards.append(current)

    return cards[:8]


def generate_study_plan(topic: str, level: str, language: str, days: int, hours_per_day: float, lesson_data: dict) -> list:
    """Generate a day-by-day study plan."""
    chapters = lesson_data.get("chapters", [])
    chapter_list = "\n".join([f"Chapter {c['number']}: {c['title']}" for c in chapters])

    response = call_groq(
        f"You are a study coach creating a {days}-day plan for learning {topic} at {level} level.",
        f"""Create a day-by-day study plan for learning "{topic}" at {level} level in {language}.

Student has: {days} days, {hours_per_day} hours/day
Chapters to cover:
{chapter_list}

For each day write:
DAY: [day number]
FOCUS: [what to study that day - specific chapter or topic]
TASKS: [3-4 specific tasks for that day]
GOAL: [what the student should be able to do after this day]

Cover all chapters across {days} days. Be realistic with time. Write in {language}.""",
        max_tokens=3000
    )

    plan = []
    current = {}
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("DAY:"):
            if current.get("day"):
                plan.append(current)
            current = {"day": line.split(":", 1)[1].strip(), "focus": "", "tasks": "", "goal": ""}
        elif line.upper().startswith("FOCUS:"):
            current["focus"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TASKS:"):
            current["tasks"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("GOAL:"):
            current["goal"] = line.split(":", 1)[1].strip()
        elif current.get("tasks") is not None and line and not any(line.upper().startswith(k) for k in ["DAY:", "FOCUS:", "GOAL:"]):
            current["tasks"] += " " + line
    if current.get("day"):
        plan.append(current)

    return plan


def generate_mock_interview(topic: str, level: str, language: str) -> list:
    """Generate mock interview questions."""
    response = call_groq(
        f"You are a senior {topic} interviewer at a top tech company.",
        f"""Create 10 interview questions for a {level}-level {topic} candidate in {language}.

Mix of:
- 3 conceptual questions (test understanding)
- 3 practical/scenario questions (test application)
- 2 problem-solving questions (test thinking)
- 2 advanced questions (test depth)

For each question:
QUESTION: [interview question specific to {topic} at {level} level]
TYPE: [Conceptual / Practical / Problem-Solving / Advanced]
IDEAL ANSWER: [what a strong candidate would say — 3-4 sentences]
RED FLAG: [what a weak answer looks like]

Write in {language}. Plain text only.""",
        max_tokens=3000
    )

    questions = []
    current = {}
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("QUESTION:"):
            if current.get("question"):
                questions.append(current)
            current = {"question": line.split(":", 1)[1].strip(), "type": "", "ideal_answer": "", "red_flag": ""}
        elif line.upper().startswith("TYPE:"):
            current["type"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("IDEAL ANSWER:"):
            current["ideal_answer"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("RED FLAG:"):
            current["red_flag"] = line.split(":", 1)[1].strip()
        elif current.get("ideal_answer") is not None and line and not any(line.upper().startswith(k) for k in ["QUESTION:", "TYPE:", "RED FLAG:"]):
            current["ideal_answer"] += " " + line
    if current.get("question"):
        questions.append(current)

    return questions[:10]


def grade_interview_answer(topic: str, question: str, answer: str, ideal_answer: str, language: str) -> dict:
    """Grade a mock interview answer."""
    response = call_groq(
        f"You are a senior {topic} interviewer giving constructive feedback.",
        f"""Grade this interview answer for a {topic} position.

Question: {question}
Student's Answer: {answer}
Ideal Answer: {ideal_answer}

Give feedback in this exact format:
SCORE: [number 1-10]
VERDICT: [Excellent / Good / Needs Work / Incorrect]
STRENGTHS: [what they got right, specific to {topic}]
IMPROVEMENTS: [what to add or fix, specific to {topic}]
TIP: [one specific tip to answer better next time]

Write in {language}. Plain text only.""",
        max_tokens=600
    )

    result = {"score": 5, "verdict": "Good", "strengths": "", "improvements": "", "tip": ""}
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("SCORE:"):
            try:
                result["score"] = int(''.join(filter(str.isdigit, line.split(":", 1)[1][:3])))
            except:
                pass
        elif line.upper().startswith("VERDICT:"):
            result["verdict"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("STRENGTHS:"):
            result["strengths"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("IMPROVEMENTS:"):
            result["improvements"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TIP:"):
            result["tip"] = line.split(":", 1)[1].strip()
    return result


def generate_cheat_sheet(topic: str, level: str, language: str, lesson_data: dict) -> str:
    """Generate a full cheat sheet / summary for the entire topic."""
    chapters = lesson_data.get("chapters", [])
    chapter_list = "\n".join([f"- {c['title']}" for c in chapters])

    return call_groq(
        f"You are an expert in {topic} writing a concise but comprehensive cheat sheet.",
        f"""Write a complete cheat sheet for "{topic}" at {level} level in {language}.

Chapters covered:
{chapter_list}

Structure it as:
## {topic} Cheat Sheet — {level} Level

### Quick Reference
[5-6 most important concepts with one-line definitions]

### Key Concepts
[For each major concept: term + 2-sentence explanation]

### Common Patterns / Formulas
[Most used patterns, syntax, or formulas in {topic}]

### Do's and Don'ts
[5 do's and 5 don'ts specific to {topic}]

### Quick Revision Questions
[5 questions to test understanding]

### Resources
[3-4 best free resources to go deeper]

Be specific to {topic}. Use real {topic} terminology. Write in {language}.""",
        max_tokens=3000
    )


# ─────────────────────────────────────────────
# AI DOUBT SOLVER
# ─────────────────────────────────────────────
def ask_doubt(topic: str, chapter_title: str, level: str, language: str, question: str, history: list) -> str:
    history_text = ""
    for msg in history[-6:]:
        role = "Student" if msg["role"] == "user" else "Teacher"
        history_text += f"{role}: {msg['content']}\n"

    return call_groq(
        f"You are an expert teacher in {topic}. You are helping a {level} student understand '{chapter_title}'. "
        f"Give clear, specific, detailed answers. Always use examples from {topic}. Never be generic. "
        f"Answer in {language}.",
        f"""Previous conversation:
{history_text}

Student's question: {question}

Answer specifically about '{chapter_title}' in {topic} for a {level} student.
Use real {topic} terminology and examples. Be thorough but clear. Write in {language}.""",
        max_tokens=1000
    )


# ─────────────────────────────────────────────
# PRACTICE PROBLEMS
# ─────────────────────────────────────────────
def generate_practice_problems(topic: str, chapter_title: str, level: str, language: str) -> list:
    response = call_groq(
        f"You are an expert problem setter for {topic}. Create practice problems that test real understanding.",
        f"""Create 5 practice problems for "{chapter_title}" in {topic} at {level} level in {language}.

Each problem must be specifically about {chapter_title} in {topic}.
Vary difficulty: Warm Up, Easy, Medium, Hard, Challenge.

Format each problem EXACTLY like this — repeat for all 5:

PROBLEM: [the full problem statement, scenario or question about {chapter_title} in {topic}]
HINT: [a helpful hint that nudges toward the answer without giving it away]
ANSWER: [detailed answer with explanation using {topic} terminology]
---

Write in {language}. Make problems progressively harder.""",
        max_tokens=3000
    )

    problems = []
    blocks = response.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        prob = {}
        for line in block.split('\n'):
            line = line.strip()
            if line.upper().startswith('PROBLEM:'):
                prob['problem'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('HINT:'):
                prob['hint'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('ANSWER:'):
                prob['answer'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif prob.get('answer') is not None and line:
                prob['answer'] = prob.get('answer', '') + ' ' + line
        if prob.get('problem'):
            problems.append(prob)

    if not problems:
        for i in range(1, 6):
            problems.append({
                'problem': f"Problem {i}: Explain how {chapter_title} works in {topic} with a real example.",
                'hint': f"Think about the core mechanism of {chapter_title} in {topic}.",
                'answer': f"{chapter_title} in {topic} involves understanding the core concept and applying it practically."
            })
    return problems[:5]


# ─────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────
def generate_flashcards(topic: str, chapter_title: str, level: str, language: str) -> list:
    response = call_groq(
        f"You are an expert in {topic} creating flashcards for {level} students.",
        f"""Create 10 flashcards for "{chapter_title}" in {topic} at {level} level in {language}.

Each flashcard must test a specific concept from {chapter_title} in {topic}.
Mix question types: definitions, how-it-works, why, examples, comparisons.

Format each card EXACTLY like this — repeat for all 10:

FRONT: [clear question or term about {chapter_title} in {topic}]
BACK: [concise but complete answer using {topic} terminology]
---

Write in {language}. Make each card specific to {topic}.""",
        max_tokens=2000
    )

    cards = []
    blocks = response.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        card = {}
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('FRONT:'):
                card['front'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('BACK:'):
                card['back'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif card.get('back') is not None and line:
                card['back'] = card.get('back', '') + ' ' + line
        if card.get('front') and card.get('back'):
            cards.append(card)

    if not cards:
        cards = [
            {'front': f"What is {chapter_title} in {topic}?", 'back': f"{chapter_title} is a core concept in {topic} that helps you understand how the system works."},
            {'front': f"Why is {chapter_title} important in {topic}?", 'back': f"{chapter_title} is essential because it forms the foundation for more advanced {topic} concepts."},
        ]
    return cards[:10]


# ─────────────────────────────────────────────
# STUDY PLAN
# ─────────────────────────────────────────────
def generate_study_plan(topic: str, level: str, language: str, days: int, hours: float, lesson_data: dict) -> list:
    chapters = lesson_data.get("chapters", [])
    chapters_text = "\n".join([f"- Chapter {c['number']}: {c['title']}" for c in chapters])

    response = call_groq(
        f"You are a study coach creating personalized plans for {topic} learners.",
        f"""Create a {days}-day study plan for learning {topic} at {level} level in {language}.
Student has {hours} hours per day.

Chapters to cover:
{chapters_text}

Distribute chapters across {days} days. Include practice, review, and rest days where appropriate.

Format each day EXACTLY like this — repeat for all {days} days:

DAY: [day number]
FOCUS: [what to study today, specific to {topic}]
TASKS: [detailed tasks for today, {hours} hours worth]
GOAL: [what the student should be able to do after today]
---

Write in {language}. Be specific to {topic} chapters listed above.""",
        max_tokens=4000
    )

    plan = []
    blocks = response.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        day = {}
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('DAY:'):
                day['day'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('FOCUS:'):
                day['focus'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('TASKS:'):
                day['tasks'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('GOAL:'):
                day['goal'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif day.get('tasks') is not None and not line.upper().startswith('GOAL:') and line:
                if not any(line.upper().startswith(k) for k in ['DAY:', 'FOCUS:', 'GOAL:']):
                    day['tasks'] = day.get('tasks', '') + ' ' + line
        if day.get('focus'):
            plan.append(day)

    return plan[:days]


# ─────────────────────────────────────────────
# MOCK INTERVIEW
# ─────────────────────────────────────────────
def generate_mock_interview(topic: str, level: str, language: str) -> list:
    response = call_groq(
        f"You are a senior technical interviewer specializing in {topic}.",
        f"""Create 6 {level}-level interview questions for {topic} in {language}.

Mix question types:
- 2 Conceptual (test understanding of {topic} concepts)
- 2 Practical (test ability to apply {topic})
- 1 Problem-Solving (scenario-based {topic} challenge)
- 1 Advanced (deep {topic} knowledge)

Format each question EXACTLY like this — repeat for all 6:

TYPE: [Conceptual / Practical / Problem-Solving / Advanced]
QUESTION: [the interview question about {topic} for {level} level]
IDEAL_ANSWER: [a comprehensive ideal answer using real {topic} terminology, 4-6 sentences]
---

Write in {language}. Questions must be specific to {topic}.""",
        max_tokens=3000
    )

    questions = []
    blocks = response.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        q = {}
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('TYPE:'):
                q['type'] = line.split(':', 1)[1].strip() if ':' in line else 'Conceptual'
            elif line.upper().startswith('QUESTION:'):
                q['question'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line.upper().startswith('IDEAL_ANSWER:'):
                q['ideal_answer'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif q.get('ideal_answer') is not None and line:
                if not any(line.upper().startswith(k) for k in ['TYPE:', 'QUESTION:']):
                    q['ideal_answer'] = q.get('ideal_answer', '') + ' ' + line
        if q.get('question'):
            questions.append(q)

    return questions[:6]


def grade_interview_answer(topic: str, question: str, user_answer: str, ideal_answer: str, language: str) -> dict:
    response = call_groq(
        f"You are a senior {topic} interviewer grading a candidate's answer.",
        f"""Grade this interview answer about {topic}.

Question: {question}
Candidate's answer: {user_answer}
Ideal answer: {ideal_answer}

Respond in this EXACT format:

SCORE: [number from 1-10]
VERDICT: [Excellent / Good / Needs Work / Incorrect]
STRENGTHS: [1-2 sentences about what was good in the answer]
IMPROVEMENTS: [1-2 sentences about what was missing or wrong]
TIP: [one specific actionable tip to improve for this type of {topic} question]

Write in {language}.""",
        max_tokens=500
    )

    grade = {'score': 5, 'verdict': 'Good', 'strengths': '', 'improvements': '', 'tip': ''}
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith('SCORE:'):
            try:
                grade['score'] = int(''.join(filter(str.isdigit, line.split(':', 1)[1][:3])))
            except Exception:
                grade['score'] = 5
        elif line.upper().startswith('VERDICT:'):
            grade['verdict'] = line.split(':', 1)[1].strip() if ':' in line else 'Good'
        elif line.upper().startswith('STRENGTHS:'):
            grade['strengths'] = line.split(':', 1)[1].strip() if ':' in line else ''
        elif line.upper().startswith('IMPROVEMENTS:'):
            grade['improvements'] = line.split(':', 1)[1].strip() if ':' in line else ''
        elif line.upper().startswith('TIP:'):
            grade['tip'] = line.split(':', 1)[1].strip() if ':' in line else ''
    return grade


# ─────────────────────────────────────────────
# CHEAT SHEET
# ─────────────────────────────────────────────
def generate_cheat_sheet(topic: str, level: str, language: str, lesson_data: dict) -> str:
    chapters = lesson_data.get("chapters", [])
    chapters_text = "\n".join([f"- {c['title']}" for c in chapters])

    return call_groq(
        f"You are an expert in {topic} writing a concise but complete cheat sheet.",
        f"""Write a comprehensive cheat sheet for {topic} at {level} level in {language}.

Chapters covered:
{chapters_text}

Structure the cheat sheet with these sections using ## headings:

## Core Concepts
## Key Terms & Definitions
## How It Works (Quick Reference)
## Common Patterns & Best Practices
## Common Mistakes to Avoid
## Quick Commands / Syntax (if applicable)
## What to Remember

For each section:
- Use bullet points (- )
- Be concise but specific to {topic}
- Use real {topic} terminology
- Make it scannable and useful as a reference

Write in {language}. Every point must be specific to {topic} — no generic advice.""",
        max_tokens=3000
    )


# ─────────────────────────────────────────────
# FLOW DIAGRAM
# ─────────────────────────────────────────────
def generate_flow_diagram(topic: str, chapter_title: str, level: str, language: str) -> dict:
    """Generate a structured, chapter-specific flow diagram."""
    system = "You are an educational diagram designer. Return only valid JSON, no markdown, no extra text."
    user = f"""Create a flow diagram that shows exactly how "{chapter_title}" works in {topic}.

Return ONLY this JSON (no markdown fences):
{{
  "nodes": [
    {{"id": 1, "label": "2-3 words", "desc": "5-7 words describing this step", "icon": "emoji"}},
    {{"id": 2, "label": "2-3 words", "desc": "5-7 words describing this step", "icon": "emoji"}},
    {{"id": 3, "label": "2-3 words", "desc": "5-7 words describing this step", "icon": "emoji"}},
    {{"id": 4, "label": "2-3 words", "desc": "5-7 words describing this step", "icon": "emoji"}}
  ],
  "connections": [
    {{"from": 1, "to": 2}},
    {{"from": 2, "to": 3}},
    {{"from": 3, "to": 4}}
  ]
}}

Rules:
- 4 to 5 nodes maximum
- Labels must name REAL steps/components of {chapter_title} in {topic} (NOT generic like "Input/Process/Output")
- Descriptions must be specific to {chapter_title} in {topic}
- Icons must be relevant emojis that visually represent each step
- Connections show the actual sequence or data flow of {chapter_title}
- Write labels and descs in {language}"""

    response = call_groq(system, user, max_tokens=600)
    result = parse_json_response(response)

    if not result or not result.get('nodes'):
        result = {
            "nodes": [
                {"id": 1, "label": chapter_title[:15], "desc": "Process starts here", "icon": "▶️"},
                {"id": 2, "label": "Core Logic", "desc": f"Main {chapter_title} logic", "icon": "⚙️"},
                {"id": 3, "label": "Transform", "desc": "Data is processed", "icon": "🔄"},
                {"id": 4, "label": "Result", "desc": "Output is produced", "icon": "✅"}
            ],
            "connections": [{"from": 1, "to": 2}, {"from": 2, "to": 3}, {"from": 3, "to": 4}]
        }
    return result
