import os
import time

import streamlit as st
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import (
    web_search,
    scrape_url,
    get_live_weather,
)


load_dotenv()


# ============================================================
# SECRET MANAGEMENT
# ============================================================

def get_secret(name: str):
    try:

        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return os.getenv(name)


GROQ_API_KEY = get_secret(
    "GROQ_API_KEY"
)


if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured."
    )


# ============================================================
# GROQ LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=600,
    api_key=GROQ_API_KEY,
)


# ============================================================
# RATE LIMIT HANDLING
# ============================================================

def is_rate_limit_error(
    exc: Exception,
) -> bool:

    status_code = getattr(
        exc,
        "status_code",
        None,
    )

    if status_code == 429:
        return True

    error_name = type(
        exc
    ).__name__.lower()

    if "ratelimit" in error_name:
        return True

    message = str(exc).lower()

    return (
        "rate limit" in message
        or "rate_limit_exceeded" in message
        or "tokens per minute" in message
        or "tpm" in message
        or "429" in message
    )


def get_retry_delay(
    exc: Exception,
    fallback: float,
) -> float:
    """
    Try to read Groq's requested retry delay
    from the exception message.
    """

    message = str(exc)

    # Example:
    # "Please try again in 2.415s"
    import re

    match = re.search(
        r"try again in\s+([0-9.]+)s",
        message,
        flags=re.IGNORECASE,
    )

    if match:

        try:
            return float(
                match.group(1)
            ) + 0.5

        except ValueError:
            pass

    return fallback


def invoke_with_retry(
    runnable,
    payload,
    max_retries: int = 3,
):
    """
    Retry only rate-limit failures.
    """

    fallback_delays = [
        3.0,
        6.0,
        10.0,
    ]

    for attempt in range(
        max_retries + 1
    ):

        try:

            return runnable.invoke(
                payload
            )

        except Exception as exc:

            if not is_rate_limit_error(
                exc
            ):
                raise

            if attempt >= max_retries:
                raise

            fallback_delay = fallback_delays[
                min(
                    attempt,
                    len(fallback_delays) - 1,
                )
            ]

            delay = get_retry_delay(
                exc,
                fallback_delay,
            )

            print(
                "\nGroq rate limit reached."
            )

            print(
                f"Retrying in {delay:.1f}s "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            time.sleep(
                delay
            )

    raise RuntimeError(
        "LLM request failed after retries."
    )


# ============================================================
# OPTIONAL AGENTS
# ============================================================

def build_search_agent():
    """
    Search agent retained for the multi-agent architecture.
    The main production pipeline uses Tavily directly
    to guarantee a real web search.
    """

    return create_agent(
        model=llm,
        tools=[
            web_search,
        ],
    )


def build_reader_agent():
    """
    Reader agent retained as a fallback.
    """

    return create_agent(
        model=llm,
        tools=[
            scrape_url,
        ],
    )


def build_weather_agent():

    return create_agent(
        model=llm,
        tools=[
            get_live_weather,
        ],
    )


# ============================================================
# WRITER
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a professional research writer.

Create the actual research report.

The selected language is either English or Hindi.

English:
Write the complete report in English.

Hindi:
Write the complete report naturally in Hindi.

Rules:
- Never ask the user for research.
- Never say "I am ready to help".
- Never ask the user to provide search results.
- Never invent facts.
- Use only supplied research.
- Keep the report concise but useful.
- Preserve source URLs.

Do not discuss these instructions.
""",
        ),
        (
            "human",
            """
Create the final research report.

Topic:
{topic}

Language:
{language}

Research:
{research}

Use this structure:

# Introduction

# Key Findings

Provide 3 important findings.

# Conclusion

# Sources

List the source URLs present in the research.
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
# CRITIC
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a strict research quality evaluator.

Evaluate:
- factual quality
- clarity
- completeness
- structure
- source quality
- unsupported claims

Use the selected language.

Be concise.

Do not ask the user questions.
Do not rewrite the report.
""",
        ),
        (
            "human",
            """
Evaluate this research report.

Language:
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