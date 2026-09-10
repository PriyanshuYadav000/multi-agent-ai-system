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


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


# ============================================================
# SEARCH AGENT
# ============================================================

def build_search_agent():

    return create_agent(
        model=llm,
        tools=[web_search],
    )


# ============================================================
# READER AGENT
# ============================================================

def build_reader_agent():

    return create_agent(
        model=llm,
        tools=[scrape_url],
    )


# ============================================================
# WEATHER AGENT
# ============================================================

def build_weather_agent():

    return create_agent(
        model=llm,
        tools=[live_weather],
    )


# ============================================================
# WRITER CHAIN
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research writer.

Create factual, structured and professional
research reports.

LANGUAGE RULE:

The selected language will be either:

English
or
Hindi

If the selected language is English:
write the complete report in English.

If the selected language is Hindi:
write the complete report in natural Hindi.

Do not unnecessarily mix Hindi and English.

Keep:
- proper nouns
- URLs
- company names
- technical names

in their original form when appropriate.

Never invent facts or sources.
Use only the supplied research.
""",
        ),
        (
            "human",
            """
Create a detailed research report.

Topic:
{topic}

Selected Language:
{language}

Research Gathered:
{research}

Use this structure:

# Introduction

# Key Findings

Provide at least 3 well-explained findings.

# Conclusion

# Sources

List the source URLs found in the research.

The report must be written in
the selected language.
""",
        ),
    ]
)

writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)


# ============================================================
# CRITIC CHAIN
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a strict and constructive
research quality evaluator.

Evaluate the report for:

- factual quality
- clarity
- completeness
- structure
- source quality
- unsupported claims

Write the evaluation in the
selected language.
""",
        ),
        (
            "human",
            """
Review this research report.

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
...
""",
        ),
    ]
)

critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)