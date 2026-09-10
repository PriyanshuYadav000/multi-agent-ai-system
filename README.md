# 🤖 Multi-Agent AI Research System

> An autonomous multi-agent AI research application that searches the live web, extracts source knowledge, generates a structured research report, and evaluates the final result with an AI critic.

## 🌐 Live Demo

🚀 **Try the deployed application:**  
https://multi-agent-ai-system-rnq6zeu2j2jdx2apsr8vvv.streamlit.app/

## 📦 Source Code

🔗 **GitHub Repository:**  
https://github.com/PriyanshuYadav000/multi-agent-ai-system

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.x-blue)
![LangChain](https://img.shields.io/badge/LangChain-Agentic%20AI-green)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)
![Tavily](https://img.shields.io/badge/Tavily-Web%20Search-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Web%20Scraping-yellow)
![OpenWeather](https://img.shields.io/badge/OpenWeather-Live%20Weather-blue)

---

# 📌 Overview

The **Multi-Agent AI Research System** is an AI-powered research application designed to automate the process of researching a topic through multiple specialized stages.

Instead of asking a single LLM to directly generate an answer, the system separates the task into multiple stages:

```text
User Query
    ↓
Query Detection
    ↓
Live Web Search
    ↓
Source Extraction
    ↓
Web Scraping
    ↓
Writer Chain
    ↓
Critic Chain
    ↓
Final Research Report

The application also supports:

🌐 Live web research using Tavily
📝 Structured AI research reports
🧠 AI-based quality evaluation
🌦️ Live weather queries using OpenWeather
🇬🇧 English output
🇮🇳 Hindi output
🎙️ Speech-to-text using Groq Whisper
🔎 Search result inspection
📖 Scraped source inspection
🚀 Streamlit deployment
🛡️ Retry and token-management logic for LLM rate limits
🧠 System Architecture
🏗️ Architecture Components
1. 🔎 Live Web Search

The research pipeline uses Tavily to retrieve current information from the web.

Research Topic
      ↓
Tavily Search
      ↓
Search Results
      ↓
Relevant Sources

The search stage collects:

Titles
URLs
Snippets
Source metadata

The search stage is kept separate from report generation so the retrieved information can be inspected before the final report is produced.

2. 📖 Source Extraction & Web Scraping

After receiving search results, the system extracts real URLs and retrieves webpage content.

Technologies used:

requests
BeautifulSoup
Search Results
      ↓
Real URL
      ↓
HTTP Request
      ↓
BeautifulSoup
      ↓
Clean Source Text

The scraper attempts to remove unnecessary webpage elements and retain readable source content.

This allows the Writer Chain to work with actual source material rather than relying only on search snippets.

3. 📝 Writer Chain

The Writer Chain generates the structured research report.

It combines:

Research topic
Tavily search results
Scraped source content

The project uses LangChain Expression Language (LCEL):

writer_chain = writer_prompt | llm | StrOutputParser()

The generated research report follows a structured format:

Introduction
    ↓
Key Findings
    ↓
Analysis
    ↓
Conclusion
    ↓
Sources
4. 🧠 Critic Chain

The Critic Chain evaluates the generated report separately from the Writer Chain.

It checks for:

Strengths
Weaknesses
Missing information
Relevance
Overall quality
Final verdict

The workflow is:

Generated Report
       ↓
   AI Critic
       ↓
Quality Evaluation

This creates a second AI perspective instead of blindly trusting the initial generated report.

5. ⚙️ Pipeline Orchestrator

pipeline.py coordinates the complete workflow.

The research pipeline passes information between stages using shared state:

state = {}

state["search_results"] = ...
state["scraped_content"] = ...
state["report"] = ...
state["feedback"] = ...

This design makes the pipeline easier to:

Debug
Test
Extend
Maintain
Monitor
6. 🌦️ Weather Workflow

Weather-related queries follow a dedicated live-data workflow.

User Weather Query
       ↓
Location Detection
       ↓
OpenWeather API
       ↓
Live Weather Data
       ↓
Groq LLM Formatting
       ↓
Streamlit Response

Example:

Weather in Delhi

The application retrieves live weather information instead of depending only on the LLM's internal knowledge.

7. 🎙️ Speech-to-Text

The Streamlit application supports microphone input using Groq Whisper.

The interaction is:

🎙️ User Speaks
      ↓
Groq Whisper
      ↓
Text Appears in Query Box
      ↓
User Reviews / Edits
      ↓
Start Research

The feature is designed specifically for speech-to-text input.

The application does not use AI text-to-speech to read the final research response aloud.

8. 🚀 Streamlit Frontend

The application provides an interactive research dashboard built with Streamlit.

The interface allows users to:

Enter a research query
Select English or Hindi
Use microphone input
Start the research pipeline
View pipeline execution
Read the final report
View AI critique
Inspect search results
Inspect scraped source content
View live weather information

The frontend uses Streamlit components for the user interface and keeps the visible application interface clean and readable.

🔄 Complete Research Workflow

A normal research request follows this sequence:

┌───────────────────────────────────────┐
│           👤 User Query               │
└────────────────────┬──────────────────┘
                     ↓
┌───────────────────────────────────────┐
│          🔎 Tavily Web Search          │
└────────────────────┬──────────────────┘
                     ↓
┌───────────────────────────────────────┐
│          🔗 Extract URLs               │
└────────────────────┬──────────────────┘
                     ↓
┌───────────────────────────────────────┐
│       📖 Scrape Web Sources            │
│       Requests + BeautifulSoup         │
└────────────────────┬──────────────────┘
                     ↓
┌───────────────────────────────────────┐
│            📝 Writer Chain             │
│              Groq + LCEL               │
└────────────────────┬──────────────────┘
                     ↓
┌───────────────────────────────────────┐
│            🧠 Critic Chain             │
│          AI Quality Evaluation         │
└────────────────────┬──────────────────┘
                     ↓
┌───────────────────────────────────────┐
│        📄 Final Research Report        │
└───────────────────────────────────────┘
🛠️ Technology Stack
🐍 Python

Python is used for:

AI pipeline development
API integration
Web scraping
Data processing
Workflow orchestration
Streamlit application development
🤖 LangChain

LangChain is used for:

Prompt templates
Tool integration
AI workflows
LCEL chains
Output parsing
LLM orchestration

Important concepts learned:

Agents
Tools
Prompt Templates
LCEL
Output Parsers
State Passing
Workflow Orchestration
⚡ Groq

Groq is used as the LLM provider for fast inference.

It is used for:

Research report generation
AI critique
Query processing
Speech-to-text through Whisper
🌐 Tavily

Tavily provides live web search capabilities.

Research Query
      ↓
Tavily API
      ↓
Search Results
      ↓
Relevant Sources

This allows the application to retrieve current web information instead of relying only on static model knowledge.

🌦️ OpenWeather

OpenWeather provides live weather information.

Location
    ↓
OpenWeather API
    ↓
Current Weather Data
🕸️ Requests + BeautifulSoup
Requests

Used to retrieve webpage content.

BeautifulSoup

Used to parse webpage HTML and extract readable text.

🎨 Streamlit

Streamlit is used to build the interactive frontend and research dashboard.

The application includes:

Query input
Language selection
Speech-to-text
Pipeline visualization
Research report
AI critique
Search results
Scraped source content
Weather responses
🔐 Environment Management

The application uses environment variables for API keys during local development.

Required variables:

GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

Never commit real API keys to GitHub.

For Streamlit Cloud deployment, these values should be added through Streamlit Secrets.

📚 What I Learned

This project helped me move beyond basic LLM API calls and understand how to build a complete AI application.

1. 🤖 Building AI Agents

Instead of:

User → LLM → Answer

the project uses a more structured process:

User
 ↓
AI Workflow
 ↓
External Tools
 ↓
Live Information
 ↓
LLM
 ↓
Structured Output
2. 🔧 Tool Calling

The project uses tools for external operations.

For example:

@tool
def web_search(query: str):
    ...

and:

@tool
def scrape_url(url: str):
    ...

This taught me how AI systems can interact with external services and data sources.

3. 🔗 LCEL

I learned how LangChain operations can be composed using the pipe operator:

writer_chain = writer_prompt | llm | StrOutputParser()

This introduced me to LangChain Expression Language (LCEL) and composable AI workflows.

4. 🧩 Multi-Agent Architecture

Complex AI tasks can be broken into specialized stages:

Search
  ↓
Read
  ↓
Write
  ↓
Critique

This makes the application easier to:

Understand
Debug
Test
Extend
5. 📦 State-Based Pipeline Design

The application passes information between stages using shared state:

state = {}

state["search_results"] = ...
state["scraped_content"] = ...
state["report"] = ...
state["feedback"] = ...

This gave me practical experience with workflow orchestration.

6. 🌐 Web Scraping + AI

The project combines traditional software engineering with AI:

HTTP Requests
      +
HTML Parsing
      +
External APIs
      +
LLM Processing
      =
AI Research Pipeline

This helped me understand how AI applications can consume real-world external data.

7. 🧠 AI Evaluation

Generating an answer and evaluating an answer are two separate problems.

The Critic Chain follows:

Generate Report
      ↓
Evaluate Report
      ↓
Identify Weaknesses
      ↓
Improve Reliability

This is an important pattern for building more reliable LLM applications.

8. 🎙️ AI Speech Input

The project also demonstrates how AI speech models can be integrated into an application.

Voice
  ↓
Whisper
  ↓
Text
  ↓
Research Pipeline

This creates a more natural way for users to interact with the research system.

9. 🚀 Production Deployment

The project is not only a local prototype.

It has been deployed using Streamlit Community Cloud and is available through a public URL.

This provided practical experience with:

Environment configuration
Secrets management
Deployment
API configuration
Production debugging
Rate-limit handling
🎯 Problem Solved

Traditional AI chat applications often follow:

User Question
      ↓
LLM
      ↓
Generated Answer

This can make it difficult to:

Gather current information
Inspect original sources
Separate research from writing
Evaluate generated results
Understand how the final answer was produced

This project addresses those problems with a dedicated research workflow.

✅ The Solution
Live Web Search
      ↓
Source Extraction
      ↓
Webpage Reading
      ↓
AI Report Generation
      ↓
AI Quality Evaluation

The user receives not only a final research report, but also:

Search results
Source URLs
Scraped source content
AI-generated critique

This makes the research process more transparent.

💡 Why This Project Matters

This project demonstrates practical experience with Agentic AI application development.

It goes beyond simply calling an LLM API and combines:

LLMs
+
LangChain
+
Tools
+
Live Web Search
+
Web Scraping
+
External APIs
+
Prompt Engineering
+
LCEL
+
Workflow Orchestration
+
AI Evaluation
+
Speech-to-Text
+
Streamlit
+
Cloud Deployment

The project demonstrates both:

Software Engineering

and

AI Engineering
📁 Project Structure
MULTI AGENT AI SYSTEM/
│
├── agents.py
│   └── LLM setup, writer chain, critic chain and agent utilities
│
├── tools.py
│   └── Tavily search, webpage scraping, weather helpers and secrets
│
├── pipeline.py
│   └── Main research and weather workflow orchestration
│
├── app.py
│   └── Streamlit frontend
│
├── requirements.txt
│   └── Python dependencies
│
├── .env
│   └── Local API credentials (not committed)
│
├── .gitignore
│   └── Ignored files and secrets
│
└── README.md
    └── Project documentation
⚙️ Installation
1. Clone the repository
git clone https://github.com/PriyanshuYadav000/multi-agent-ai-system.git
cd multi-agent-ai-system
2. Create a virtual environment

Using uv:

uv venv
3. Activate the environment
macOS / Linux
source .venv/bin/activate
Windows
.venv\Scripts\activate
4. Install dependencies
uv pip install -r requirements.txt
🔐 Environment Variables

Create a .env file:

GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

Never commit your .env file.

Make sure .env is included in .gitignore.

▶️ Run the Application

Start the Streamlit application:

streamlit run app.py

The application will open in your browser.

☁️ Deployment

The current production version is deployed on Streamlit Community Cloud.

🌐 Live Application

🚀 https://multi-agent-ai-system-rnq6zeu2j2jdx2apsr8vvv.streamlit.app/

Streamlit Secrets

Configure the following secrets in Streamlit Community Cloud:

GROQ_API_KEY = "your_groq_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
OPENWEATHER_API_KEY = "your_openweather_api_key"
🧪 Example Queries
Research Query
Impact of AI on software engineering in 2026
Current Information
Latest developments in artificial intelligence
Hindi Research
भारत में आर्टिफिशियल इंटेलिजेंस का भविष्य
Weather
Weather in Delhi
Voice Input
🎙️ Speak your research question

The speech is converted into text and placed inside the research query field before execution.

📊 Expected Output

For a research query, the application provides:

📄 Research Report
        +
🧠 AI Critique
        +
🔎 Search Results
        +
📖 Scraped Sources

This makes the research workflow more transparent than returning only a final LLM response.

🛡️ Reliability & Error Handling

During development, the application encountered issues such as:

LLM rate limits
Large prompts
Too many output tokens
Irrelevant search results
Unavailable webpages
Missing environment variables
Streamlit widget state conflicts

The system was improved with:

Smaller LLM contexts
Output token limits
Retry and backoff logic
Direct Tavily retrieval
Real URL extraction
Source validation
Environment fallback handling
Safer Streamlit state management

These improvements made the application more suitable for real-world usage.

🚀 Future Improvements

Potential future improvements include:

Parallel research agents
Multiple-source extraction
Source credibility scoring
Citation verification
Research memory
Persistent research history
Database integration
Authentication
Human-in-the-loop review
Structured JSON outputs
Advanced observability
Better source validation
Improved evaluation pipelines
Scalable infrastructure
Research history and user accounts
📈 Project Learning Journey

This project represents a progression from basic LLM applications toward a complete AI application:

LLM API
   ↓
Prompt Engineering
   ↓
LangChain
   ↓
Tools
   ↓
Agents
   ↓
Multi-Stage Workflow
   ↓
External Data
   ↓
Web Scraping
   ↓
AI Evaluation
   ↓
Speech-to-Text
   ↓
Streamlit Application
   ↓
Production Deployment
👨‍💻 Author
Priyanshu Yadav

Aspiring Software Engineer focused on:

Python
JavaScript
SQL
MERN
Generative AI
LangChain
Agentic AI
⭐ Project Goal

The goal of this project is to understand how modern AI systems can move from simple:

Question → Answer

interactions toward collaborative, tool-using, evaluative workflows.

The core idea is:

SEARCH → READ → WRITE → CRITIQUE

combined with:

Live Data
+
External Tools
+
LLMs
+
AI Evaluation
+
User Interface

Built to learn. Built to experiment. Built to understand Agentic AI.

🌐 Try It Live

🚀 Multi-Agent AI Research System:
https://multi-agent-ai-system-rnq6zeu2j2jdx2apsr8vvv.streamlit.app/

⭐ If you find this project useful, consider giving the repository a star!