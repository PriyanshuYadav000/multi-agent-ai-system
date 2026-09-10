from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain,
)

from tools import (
    get_live_weather,
    is_weather_query,
    extract_weather_location,
)


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_research_pipeline(
    topic: str,
    language: str = "English",
    progress_callback=None,
) -> dict:

    topic = topic.strip()

    state = {}

    def progress(
        stage: str,
        status: str,
    ):

        if progress_callback:
            progress_callback(
                stage,
                status,
            )

    # ========================================================
    # WEATHER MODE
    # ========================================================

    if is_weather_query(topic):

        progress(
            "weather",
            "active",
        )

        location = extract_weather_location(
            topic
        )

        weather_data = get_live_weather(
            location
        )

        # Ask Groq to present weather
        # in the selected language.
        from agents import llm

        weather_prompt = f"""
You are a weather assistant.

Return the following live weather
information in {language}.

Be concise and easy to understand.

Weather data:
{weather_data}
"""

        response = llm.invoke(
            weather_prompt
        )

        answer = response.content

        state["mode"] = "weather"
        state["topic"] = topic
        state["language"] = language
        state["weather"] = answer
        state["report"] = answer
        state["feedback"] = ""
        state["search_results"] = ""
        state["scraped_content"] = ""

        progress(
            "weather",
            "complete",
        )

        return state

    # ========================================================
    # STEP 1 - SEARCH
    # ========================================================

    progress(
        "search",
        "active",
    )

    print(
        "\n" + "=" * 50
    )

    print(
        "STEP 1 - SEARCH AGENT"
    )

    print(
        "=" * 50
    )

    search_agent = build_search_agent()

    search_result = search_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    (
                        "Find recent, reliable and "
                        f"detailed information about: {topic}"
                    ),
                )
            ]
        }
    )

    state["search_results"] = (
        search_result["messages"][-1].content
    )

    progress(
        "search",
        "complete",
    )

    # ========================================================
    # STEP 2 - READER
    # ========================================================

    progress(
        "reader",
        "active",
    )

    print(
        "\n" + "=" * 50
    )

    print(
        "STEP 2 - READER AGENT"
    )

    print(
        "=" * 50
    )

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    (
                        f"Based on the following search "
                        f"results about '{topic}', "
                        "pick the most relevant URL "
                        "and scrape it for deeper content.\n\n"
                        "Search Results:\n"
                        f"{state['search_results'][:1500]}"
                    ),
                )
            ]
        }
    )

    state["scraped_content"] = (
        reader_result["messages"][-1].content
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
        "active",
    )

    print(
        "\n" + "=" * 50
    )

    print(
        "STEP 3 - WRITER CHAIN"
    )

    print(
        "=" * 50
    )

    combined_research = (
        "SEARCH RESULTS:\n"
        f"{state['search_results']}\n\n"
        "DETAILED SCRAPED CONTENT:\n"
        f"{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke(
        {
            "topic": topic,
            "language": language,
            "research": combined_research,
        }
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
        "active",
    )

    print(
        "\n" + "=" * 50
    )

    print(
        "STEP 4 - CRITIC CHAIN"
    )

    print(
        "=" * 50
    )

    state["feedback"] = critic_chain.invoke(
        {
            "report": state["report"],
            "language": language,
        }
    )

    progress(
        "critic",
        "complete",
    )

    # ========================================================
    # FINAL STATE
    # ========================================================

    state["mode"] = "research"
    state["topic"] = topic
    state["language"] = language

    return state


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    topic = input(
        "\nEnter a research topic: "
    )

    language = input(
        "Language (English/Hindi): "
    ).strip()

    if language not in [
        "English",
        "Hindi",
    ]:
        language = "English"

    result = run_research_pipeline(
        topic,
        language,
    )

    print(
        "\n\nFINAL REPORT\n"
    )

    print(
        result["report"]
    )