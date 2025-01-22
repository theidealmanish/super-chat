# 🧠 Super Chat: Talk to Websites, Simplified

Super Chat is an AI-powered assistant that transforms how you interact with website content. By simply uploading a sitemap or providing a list of URLs, Super Chat retrieves relevant information and generates concise, contextually accurate answers using state-of-the-art AI tools.

## 🚀 Features

- **Upload and Query**: Easily upload sitemaps or URLs and start querying instantly.
- **Powered by AI**: Combines **Cortex Search** for retrieval with **Mistral LLM** for natural language generation.
- **Feedback Integration**: Enhanced response quality using **TruLens** feedback-driven observability and guardrails.
- **Smart Context Management**: Maintains context across conversations for more accurate responses.
- **Intuitive Interface**: Built with Streamlit for an effortless and interactive user experience.

---

## 🎯 Inspiration

Super Chat was born out of a passion for productivity and a desire to simplify the overwhelming task of searching through endless documentation and web pages. Whether you're a developer, researcher, or just someone seeking information, Super Chat saves time and makes knowledge accessible in seconds.

---

## 📖 How It Works

1. **Ingest Website Data**: Process sitemaps or URLs and chunk the content for efficient retrieval.
2. **Ask Questions**: Query using natural language, and let the AI retrieve and generate accurate responses.
3. **Feedback-Driven Optimization**: Ensure high-quality responses using **TruLens** observability and guardrails.

---

## 🛠️ Tech Stack

- **Backend**: Snowflake Cortex Search, Mistral LLM
- **Frontend**: Streamlit Community Cloud
- **Feedback & Observability**: TruLens
- **Data Processing**: LangChain for chunking, Snowflake for storage and automation

---

## 📝 Requirements

- Python 3.8 or higher
- Snowflake account with access to Cortex Search

---

## 💻 Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/theidealmanish/super-chat.git
   cd super-chat
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Update the envs**:
   ```bash
   cp .env.example .env
   ```
4. **Run the App**:
   ```bash
   streamlit run 🏠_Home.py
   ```
