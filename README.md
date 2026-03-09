# 🧠 LearnAI — Your Personal AI Teacher

A Streamlit app that generates complete, personalized lessons on any technology topic using Claude AI. No searching, no YouTube hunting — just enter a topic and get a full lesson with explanations, analogies, examples, visual diagrams, a quiz, and a certification roadmap.

---

## ✨ Features

- 🤖 **AI-Generated Lessons** — Full 5-chapter lesson plans on any topic
- 🌍 **12 Languages** — Learn in English, Hindi, Urdu, Arabic, French, Spanish & more
- 📊 **3 Difficulty Levels** — Beginner, Intermediate, Advanced
- 💡 **Simple Explanations** — Plain English, no jargon
- 🌟 **Real-Life Analogies** — Everyday comparisons that make concepts click
- 📋 **Step-by-Step Examples** — Concrete walkthroughs of every concept
- 🎨 **Visual Diagrams** — ASCII art diagrams for every chapter
- 🧪 **AI-Generated Quiz** — 5 questions with explanations
- 🏆 **Certification Roadmap** — Real certs + personalized learning path

---

## 🚀 Quick Start (Local)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your API Key

Edit `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

Get your API key from: https://console.anthropic.com

### 3. Run the App

```bash
streamlit run app.py
```

Open your browser at: http://localhost:8501

---

## ☁️ Deploy on Streamlit Cloud (Free)

### Step 1 — Push to GitHub

1. Create a new GitHub repository
2. Upload all project files to the repo
3. Make sure the structure looks like this:

```
your-repo/
├── app.py
├── requirements.txt
├── pages/
│   ├── __init__.py
│   ├── home.py
│   ├── lesson.py
│   ├── quiz.py
│   └── certification.py
├── utils/
│   ├── __init__.py
│   └── ai_utils.py
└── .streamlit/
    └── config.toml
```

> ⚠️ Do NOT push `secrets.toml` to GitHub — it contains your API key!

### Step 2 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Connect your GitHub account
4. Select your repository
5. Set **Main file path** to: `app.py`
6. Click **"Advanced settings"**
7. Under **Secrets**, paste:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

8. Click **"Deploy!"**

Your app will be live at: `https://your-app-name.streamlit.app`

---

## 📁 Project Structure

```
learnai/
├── app.py                  # Main entry point, routing, global CSS
├── requirements.txt        # Python dependencies
├── pages/
│   ├── home.py             # Home screen with topic input
│   ├── lesson.py           # Lesson viewer (syllabus + chapters)
│   ├── quiz.py             # Interactive quiz
│   └── certification.py    # Certification roadmap
├── utils/
│   └── ai_utils.py         # All Claude API calls
└── .streamlit/
    ├── config.toml         # Streamlit theme config
    └── secrets.toml        # API keys (local only, don't commit)
```

---

## 🔑 Getting an Anthropic API Key

1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Click **"API Keys"** in the left sidebar
4. Click **"Create Key"**
5. Copy the key (starts with `sk-ant-...`)
6. Paste it in your secrets

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io) — Web framework
- [Anthropic Claude](https://anthropic.com) — AI model (claude-opus-4-5)
- Python 3.9+

---

## 💡 Usage Tips

- **Be specific** with topics: "React Hooks" works better than just "React"
- **Start with Beginner** even if experienced — great for quick overviews
- **Use your native language** for the most natural explanations
- **Review chapters** before taking the quiz for best results
