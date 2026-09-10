import os
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import (
    web_search,
    scrape_url,
    live_weather,
)

load_dotenv()

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured.")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1000,
    api_key=GROQ_API_KEY,
)

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )

def build_weather_agent():
    return create_agent(
        model=llm,
        tools=[live_weather],
    )

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert research writer.

Create factual, structured and professional research reports.

The selected language is either English or Hindi.

Write the complete report in the selected language.
Do not unnecessarily mix languages.

Keep proper nouns, URLs, company names and technical names
in their original form when appropriate.

Never invent facts or sources.
Use only the supplied research."""
    ),
    (
        "human",
        """Create a research report.

Topic:
{topic}

Selected Language:
{language}

Research:
{research}

Structure:

# Introduction

# Key Findings

Provide at least 3 well-explained findings.

# Conclusion

# Sources

List the source URLs found in the research.

Write the complete report in the selected language."""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a strict and constructive research quality evaluator.

Evaluate:
- factual quality
- clarity
- completeness
- structure
- source quality
- unsupported claims

Write the evaluation in the selected language."""
    ),
    (
        "human",
        """Review this research report.

Selected Language:
{language}

Report:
{report}

Return exactly:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()