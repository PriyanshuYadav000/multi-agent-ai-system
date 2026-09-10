import re

from agents import (
    build_reader_agent,
    critic_chain,
    invoke_with_retry,
    llm,
    writer_chain,
)

from tools import (
    extract_weather_location,
    get_live_weather,
    is_weather_query,
    scrape_url,
    web_search,
)


# ============================================================
# MESSAGE CONTENT
# ============================================================

def get_message_content(
    message,
) -> str:
    """
    Safely extract text from a LangChain response.
    """

    if message is None:
        return ""

    content = getattr(
        message,
        "content",
        message,
    )

    if isinstance(
        content,
        str,
    ):
        return content.strip()

    if isinstance(
        content,
        list,
    ):

        parts = []

        for item in content:

            if isinstance(
                item,
                str,
            ):
                parts.append(item)

            elif isinstance(
                item,
                dict,
            ):

                text = item.get(
                    "text"
                )

                if text:
                    parts.append(
                        str(text)
                    )

        return "\n".join(
            parts
        ).strip()

    return str(
        content
    ).strip()


# ============================================================
# TEXT LIMITER
# ============================================================

def limit_text(
    text: str,
    max_chars: int,
) -> str:

    if not text:
        return ""

    text = str(
        text
    )

    if len(text) <= max_chars:
        return text

    return (
        text[:max_chars]
        + "\n\n[Content truncated.]"
    )


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_urls(
    text: str,
) -> list[str]:
    """
    Extract unique HTTP/HTTPS URLs.
    """

    if not text:
        return []

    urls = re.findall(
        r"https?://[^\s<>\]\)\"']+",
        text,
    )

    clean_urls = []

    for url in urls:

        url = url.rstrip(
            ".,;:!?)]}>"
        )

        if url not in clean_urls:
            clean_urls.append(url)

    return clean_urls


# ============================================================
# SAFE STRING
# ============================================================

def safe_string(
    value,
    default: str = "",
) -> str:

    if value is None:
        return default

    if isinstance(
        value,
        str,
    ):
        return value.strip()

    return str(
        value
    ).strip()


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_research_pipeline(
    topic: str,
    language: str = "English",
    progress_callback=None,
) -> dict:
    """
    Production research pipeline.

    Normal research:

        Tavily
          ↓
        URLs
          ↓
        Source scraping
          ↓
        Writer
          ↓
        Critic

    Weather:

        Weather detection
          ↓
        OpenWeather
          ↓
        LLM formatting
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    topic = safe_string(
        topic
    )

    if not topic:

        raise ValueError(
            "Research topic cannot be empty."
        )

    if language not in {
        "English",
        "Hindi",
    }:

        language = "English"

    # ========================================================
    # STATE
    # ========================================================

    state = {
        "mode": "",
        "topic": topic,
        "language": language,
        "weather": "",
        "search_results": "",
        "scraped_content": "",
        "report": "",
        "feedback": "",
    }

    # ========================================================
    # PROGRESS
    # ========================================================

    def progress(
        stage,
        status,
    ):

        if progress_callback:

            progress_callback(
                stage,
                status,
            )

    # ========================================================
    # WEATHER
    # ========================================================

    if is_weather_query(
        topic
    ):

        progress(
            "weather",
            "running",
        )

        print(
            "\n" + "=" * 60
        )

        print(
            "WEATHER MODE"
        )

        print(
            "=" * 60
        )

        location = extract_weather_location(
            topic
        )

        print(
            f"Weather location: {location}"
        )

        if not location:

            state["mode"] = "weather"

            state["weather"] = (
                "Please provide a city or location "
                "for the weather search."
            )

            state["report"] = (
                state["weather"]
            )

            progress(
                "weather",
                "complete",
            )

            return state

        weather_data = get_live_weather.invoke(
            location
        )

        weather_data = limit_text(
            weather_data,
            1500,
        )

        weather_prompt = f"""
You are a weather assistant.

Present the following live weather information
in {language}.

Rules:
- Be concise.
- Be accurate.
- Do not invent information.
- Do not change numerical values.
- Do not ask questions.

Weather data:

{weather_data}
"""

        response = invoke_with_retry(
            llm,
            weather_prompt,
        )

        answer = get_message_content(
            response
        )

        if not answer:

            answer = weather_data

        state["mode"] = "weather"

        state["weather"] = answer

        state["report"] = answer

        progress(
            "weather",
            "complete",
        )

        return state

    # ========================================================
    # RESEARCH MODE
    # ========================================================

    state["mode"] = "research"

    # ========================================================
    # STEP 1 - DIRECT TAVILY SEARCH
    # ========================================================

    progress(
        "search",
        "running",
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 1 - DIRECT TAVILY SEARCH"
    )

    print(
        "=" * 60
    )

    try:

        # DIRECT TOOL CALL.
        # This guarantees that a real web search occurs.
        search_output = web_search.invoke(
            topic
        )

        state["search_results"] = safe_string(
            search_output
        )

    except Exception as exc:

        print(
            f"Search failed: {exc}"
        )

        state["search_results"] = (
            f"Search failed: {exc}"
        )

    state["search_results"] = limit_text(
        state["search_results"],
        5000,
    )

    if not state["search_results"]:

        state["search_results"] = (
            "No search results were returned."
        )

    print(
        "\nSEARCH RESULTS:\n"
    )

    print(
        state["search_results"]
    )

    # --------------------------------------------------------
    # Extract URLs
    # --------------------------------------------------------

    urls = extract_urls(
        state["search_results"]
    )

    print(
        f"\nFound {len(urls)} URLs."
    )

    progress(
        "search",
        "complete",
    )

    # ========================================================
    # STEP 2 - SOURCE READING
    # ========================================================

    progress(
        "reader",
        "running",
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 2 - SOURCE READING"
    )

    print(
        "=" * 60
    )

    scraped_content = ""

    # --------------------------------------------------------
    # Try the first real search result.
    # --------------------------------------------------------

    if urls:

        for selected_url in urls[:3]:

            print(
                f"\nTrying source:"
                f"\n{selected_url}"
            )

            try:

                source = scrape_url.invoke(
                    selected_url
                )

                source = safe_string(
                    source
                )

                # Reject common scraping failures.
                if (
                    source
                    and not source.startswith(
                        "Could not scrape"
                    )
                    and not source.startswith(
                        "URL is empty"
                    )
                ):

                    scraped_content = source

                    print(
                        f"Source successfully scraped."
                    )

                    break

            except Exception as exc:

                print(
                    f"Scraping failed: {exc}"
                )

    # --------------------------------------------------------
    # Fallback Reader Agent.
    # --------------------------------------------------------

    if not scraped_content:

        print(
            "\nUsing Reader Agent fallback..."
        )

        try:

            reader_agent = build_reader_agent()

            reader_prompt = (
                "You are a source reader.\n\n"
                "Here are the real web search results:\n\n"
                f"{limit_text(state['search_results'], 2500)}\n\n"
                "Identify the most relevant URL and use "
                "the scrape_url tool on it.\n"
                "Return the actual source content.\n"
                "Do not ask the user for information."
            )

            reader_result = invoke_with_retry(
                reader_agent,
                {
                    "messages": [
                        (
                            "user",
                            reader_prompt,
                        )
                    ]
                },
            )

            reader_messages = (
                reader_result.get(
                    "messages",
                    [],
                )
                if isinstance(
                    reader_result,
                    dict,
                )
                else []
            )

            if reader_messages:

                scraped_content = (
                    get_message_content(
                        reader_messages[-1]
                    )
                )

            else:

                scraped_content = (
                    get_message_content(
                        reader_result
                    )
                )

        except Exception as exc:

            print(
                f"Reader fallback failed: {exc}"
            )

    # --------------------------------------------------------
    # Final reader fallback.
    # --------------------------------------------------------

    scraped_content = safe_string(
        scraped_content
    )

    if not scraped_content:

        scraped_content = (
            "No webpage could be scraped. "
            "Use the search results as the available evidence."
        )

    state["scraped_content"] = limit_text(
        scraped_content,
        5000,
    )

    print(
        "\nSOURCE CONTENT LENGTH:",
        len(
            state["scraped_content"]
        ),
    )

    progress(
        "reader",
        "complete",
    )

    # ========================================================
    # STEP 3 - WRITER
    # ========================================================

    progress(
        "writer",
        "running",
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 3 - WRITER"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Strict token control.
    # --------------------------------------------------------

    search_for_writer = limit_text(
        state["search_results"],
        1600,
    )

    source_for_writer = limit_text(
        state["scraped_content"],
        2500,
    )

    combined_research = (
        "SEARCH RESULTS:\n"
        f"{search_for_writer}\n\n"
        "SCRAPED SOURCE:\n"
        f"{source_for_writer}"
    )

    try:

        writer_response = invoke_with_retry(
            writer_chain,
            {
                "topic": limit_text(
                    topic,
                    400,
                ),
                "language": language,
                "research": combined_research,
            },
        )

        state["report"] = get_message_content(
            writer_response
        )

    except Exception as exc:

        print(
            f"Writer failed: {exc}"
        )

        # ----------------------------------------------------
        # Smaller emergency writer request.
        # ----------------------------------------------------

        emergency_prompt = f"""
Write a concise factual research report.

Topic:
{limit_text(topic, 300)}

Language:
{language}

Evidence:
{limit_text(combined_research, 3000)}

Use:

# Introduction

# Key Findings

# Conclusion

# Sources

Do not ask questions.
Do not invent facts.
"""

        emergency_response = invoke_with_retry(
            llm,
            emergency_prompt,
        )

        state["report"] = (
            get_message_content(
                emergency_response
            )
        )

    state["report"] = safe_string(
        state["report"]
    )

    if not state["report"]:

        state["report"] = (
            "The research report could not be generated."
        )

    state["report"] = limit_text(
        state["report"],
        6500,
    )

    print(
        "\nWRITER OUTPUT:\n"
    )

    print(
        state["report"]
    )

    progress(
        "writer",
        "complete",
    )

    # ========================================================
    # STEP 4 - CRITIC
    # ========================================================

    progress(
        "critic",
        "running",
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "STEP 4 - CRITIC"
    )

    print(
        "=" * 60
    )

    try:

        critic_response = invoke_with_retry(
            critic_chain,
            {
                "report": limit_text(
                    state["report"],
                    3500,
                ),
                "language": language,
            },
        )

        state["feedback"] = (
            get_message_content(
                critic_response
            )
        )

    except Exception as exc:

        print(
            f"Critic failed: {exc}"
        )

        emergency_critic_prompt = f"""
Evaluate this research report.

Language:
{language}

Report:
{limit_text(state["report"], 3000)}

Return:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
"""

        emergency_critic_response = (
            invoke_with_retry(
                llm,
                emergency_critic_prompt,
            )
        )

        state["feedback"] = (
            get_message_content(
                emergency_critic_response
            )
        )

    state["feedback"] = safe_string(
        state["feedback"]
    )

    if not state["feedback"]:

        state["feedback"] = (
            "The research critique could not be generated."
        )

    state["feedback"] = limit_text(
        state["feedback"],
        3000,
    )

    print(
        "\nCRITIC OUTPUT:\n"
    )

    print(
        state["feedback"]
    )

    progress(
        "critic",
        "complete",
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    return state


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    topic = input(
        "\nEnter a research topic: "
    ).strip()

    language = input(
        "Language (English/Hindi): "
    ).strip()

    if language not in {
        "English",
        "Hindi",
    }:
        language = "English"

    result = run_research_pipeline(
        topic=topic,
        language=language,
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "FINAL REPORT"
    )

    print(
        "=" * 60
    )

    print(
        result.get(
            "report",
            "",
        )
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "CRITIC FEEDBACK"
    )

    print(
        "=" * 60
    )

    print(
        result.get(
            "feedback",
            "",
        )
    )