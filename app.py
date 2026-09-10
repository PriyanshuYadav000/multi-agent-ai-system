import os
import streamlit as st

from groq import Groq
from streamlit_mic_recorder import mic_recorder

from pipeline import run_research_pipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Agent AI Research System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SECRET MANAGEMENT
# ============================================================

def get_secret(name: str):
    """
    Read from Streamlit secrets first.
    Fall back to environment variables.
    """
    try:
        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return os.getenv(name)


GROQ_API_KEY = get_secret("GROQ_API_KEY")


if not GROQ_API_KEY:
    st.error(
        "GROQ_API_KEY is not configured."
    )
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

if "voice_query" not in st.session_state:
    st.session_state.voice_query = ""

if "result" not in st.session_state:
    st.session_state.result = None

if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False

if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"


# ============================================================
# PAGE TITLE
# ============================================================

st.write("")

st.caption(
    "● AUTONOMOUS MULTI-AGENT RESEARCH"
)

st.title(
    "Multi-Agent AI Research System"
)

st.write(
    "Search the live web, read real sources, "
    "generate structured research, evaluate the result, "
    "and interact with the AI using English or Hindi voice."
)


# ============================================================
# RESEARCH CONSOLE
# ============================================================

with st.container(border=True):

    header_col, meta_col = st.columns(
        [4, 1]
    )

    with header_col:

        st.subheader(
            "🔎 Research Intelligence Console"
        )

    with meta_col:

        st.caption(
            "MULTI_AGENT_PIPELINE :: READY"
        )

    st.caption(
        "ENTER YOUR RESEARCH QUERY"
    )


# ============================================================
# VOICE QUERY HANDOFF
# ============================================================

if st.session_state.voice_query:

    st.session_state.query_input = (
        st.session_state.voice_query
    )

    st.session_state.voice_query = ""


# ============================================================
# QUERY INPUT
# ============================================================

topic = st.text_input(
    "Research query",
    placeholder=(
        "Ask anything... "
        "e.g. Latest AI developments in 2026"
    ),
    key="query_input",
)


# ============================================================
# LANGUAGE + START
# ============================================================

language_col, button_col = st.columns(
    [1, 1]
)


with language_col:

    language = st.selectbox(
        "Response language",
        [
            "English",
            "Hindi",
        ],
        index=(
            1
            if st.session_state.selected_language == "Hindi"
            else 0
        ),
    )

    st.session_state.selected_language = language


with button_col:

    run_button = st.button(
        "🚀 START RESEARCH",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.pipeline_running,
    )


# ============================================================
# VOICE INFORMATION
# ============================================================

st.info(
    "🎙️ Speak your question → AI converts your speech "
    "into text → review the text → start research."
)


# ============================================================
# MICROPHONE
# ============================================================

audio = mic_recorder(
    start_prompt="🎙️ START SPEAKING",
    stop_prompt="⏹️ STOP RECORDING",
    just_once=True,
    use_container_width=True,
    format="webm",
    key="research_mic",
)


# ============================================================
# SPEECH → TEXT
# ============================================================

if audio:

    try:

        with st.spinner(
            "Converting speech to text..."
        ):

            client = Groq(
                api_key=GROQ_API_KEY
            )

            language_code = (
                "hi"
                if language == "Hindi"
                else "en"
            )

            transcription = (
                client
                .audio
                .transcriptions
                .create(
                    file=(
                        "recording.webm",
                        audio["bytes"],
                    ),
                    model="whisper-large-v3-turbo",
                    language=language_code,
                    response_format="json",
                    temperature=0,
                )
            )

            transcript = getattr(
                transcription,
                "text",
                "",
            ).strip()

        if transcript:

            st.session_state.voice_query = (
                transcript
            )

            st.success(
                f"Transcribed text: {transcript}"
            )

            st.rerun()

        else:

            st.warning(
                "No speech was detected."
            )

    except Exception as exc:

        st.error(
            f"Speech-to-text failed: {exc}"
        )


# ============================================================
# PIPELINE DEFINITIONS
# ============================================================

RESEARCH_PHASES = [
    (
        "search",
        "🔎",
        "SEARCH AGENT",
        "WEB DISCOVERY",
    ),
    (
        "reader",
        "📖",
        "READER",
        "SOURCE EXTRACTION",
    ),
    (
        "writer",
        "✍️",
        "WRITER",
        "REPORT GENERATION",
    ),
    (
        "critic",
        "🧠",
        "CRITIC",
        "QUALITY EVALUATION",
    ),
]


WEATHER_PHASE = [
    (
        "weather",
        "🌤️",
        "WEATHER",
        "LIVE WEATHER",
    )
]


# ============================================================
# PIPELINE RENDERER
# ============================================================

def render_pipeline(
    placeholder,
    active_stage=None,
    completed=None,
    weather_mode=False,
):
    """
    Render pipeline using native Streamlit components only.
    """

    completed = completed or set()

    phases = (
        WEATHER_PHASE
        if weather_mode
        else RESEARCH_PHASES
    )

    with placeholder.container():

        st.subheader(
            "⚡ Pipeline Execution"
        )

        columns = st.columns(
            len(phases)
        )

        for index, phase in enumerate(
            phases
        ):

            key, icon, name, subtitle = (
                phase
            )

            with columns[index]:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {icon} {name}"
                    )

                    st.caption(
                        subtitle
                    )

                    if key in completed:

                        st.success(
                            "✅ COMPLETE"
                        )

                    elif key == active_stage:

                        st.info(
                            "🔄 RUNNING"
                        )

                    else:

                        st.caption(
                            "⏳ WAITING"
                        )


# ============================================================
# PIPELINE PROGRESS CALLBACK
# ============================================================

def make_progress_callback(
    placeholder,
    weather_mode=False,
):

    completed = set()

    ordered_phases = (
        ["weather"]
        if weather_mode
        else [
            "search",
            "reader",
            "writer",
            "critic",
        ]
    )

    stage_map = {
        "search": "search",
        "search_agent": "search",

        "reader": "reader",
        "reader_agent": "reader",

        "writer": "writer",
        "writer_chain": "writer",

        "critic": "critic",
        "critic_chain": "critic",

        "weather": "weather",
    }

    def callback(
        stage,
        status,
    ):

        stage = str(
            stage
        ).lower().strip()

        status = str(
            status
        ).lower().strip()

        stage = stage_map.get(
            stage,
            stage,
        )

        if stage not in ordered_phases:
            return

        if status in {
            "complete",
            "completed",
            "done",
            "finished",
        }:

            completed.add(
                stage
            )

            next_stage = None

            for phase in ordered_phases:

                if phase not in completed:

                    next_stage = phase

                    break

            render_pipeline(
                placeholder=placeholder,
                active_stage=next_stage,
                completed=completed,
                weather_mode=weather_mode,
            )

        elif status in {
            "running",
            "start",
            "started",
            "in_progress",
        }:

            render_pipeline(
                placeholder=placeholder,
                active_stage=stage,
                completed=completed,
                weather_mode=weather_mode,
            )

    return callback


# ============================================================
# RUN PIPELINE
# ============================================================

if run_button:

    query_text = topic.strip()

    if not query_text:

        st.warning(
            "Please enter a query or use the microphone."
        )

        st.stop()

    st.session_state.pipeline_running = True

    # --------------------------------------------------------
    # Weather detection for UI
    # --------------------------------------------------------

    weather_words = [
        "weather",
        "temperature",
        "forecast",
        "climate",
        "humidity",
        "rain",
        "raining",
        "snow",
        "snowing",
        "wind",
        "storm",
        "thunderstorm",
        "hot",
        "cold",
        "heat",
        "sunny",
        "cloudy",
        "monsoon",
        "बारिश",
        "मौसम",
        "तापमान",
        "ठंड",
        "गर्मी",
        "आंधी",
        "तूफान",
    ]

    query_lower = query_text.lower()

    weather_mode_ui = any(
        word in query_lower
        for word in weather_words
    )

    # --------------------------------------------------------
    # ONE pipeline placeholder
    # --------------------------------------------------------

    progress_placeholder = st.empty()

    render_pipeline(
        progress_placeholder,
        active_stage=(
            "weather"
            if weather_mode_ui
            else "search"
        ),
        completed=set(),
        weather_mode=weather_mode_ui,
    )

    try:

        with st.status(
            "AI pipeline is running...",
            expanded=True,
        ) as status:

            status.write(
                "Initializing pipeline..."
            )

            callback = make_progress_callback(
                progress_placeholder,
                weather_mode=weather_mode_ui,
            )

            result = run_research_pipeline(
                topic=query_text,
                language=language,
                progress_callback=callback,
            )

            actual_mode = result.get(
                "mode",
                "research",
            )

            # ------------------------------------------------
            # Final pipeline state
            # ------------------------------------------------

            if actual_mode == "weather":

                render_pipeline(
                    progress_placeholder,
                    active_stage=None,
                    completed={"weather"},
                    weather_mode=True,
                )

            else:

                render_pipeline(
                    progress_placeholder,
                    active_stage=None,
                    completed={
                        "search",
                        "reader",
                        "writer",
                        "critic",
                    },
                    weather_mode=False,
                )

            status.update(
                label="✅ Processing complete",
                state="complete",
                expanded=False,
            )

        st.session_state.result = result

    except Exception as exc:

        st.error(
            f"Pipeline failed: {exc}"
        )

        with st.expander(
            "🔧 Technical error details"
        ):

            st.exception(exc)

    finally:

        st.session_state.pipeline_running = False


# ============================================================
# RESULTS
# ============================================================

result = st.session_state.result


if result:

    st.divider()

    mode = result.get(
        "mode",
        "research",
    )

    # ========================================================
    # WEATHER
    # ========================================================

    if mode == "weather":

        with st.container(
            border=True
        ):

            st.subheader(
                "🌤️ Live Weather"
            )

            weather_text = str(
                result.get(
                    "weather",
                    result.get(
                        "report",
                        "",
                    ),
                )
            ).strip()

            if weather_text:

                st.markdown(
                    weather_text
                )

            else:

                st.warning(
                    "No weather result was returned."
                )

    # ========================================================
    # RESEARCH
    # ========================================================

    else:

        with st.container(
            border=True
        ):

            st.subheader(
                "📄 Generated Research"
            )

            tabs = st.tabs(
                [
                    "📄 Research Report",
                    "🧠 Critique",
                    "🔎 Search Results",
                    "📖 Scraped Sources",
                ]
            )

            # ------------------------------------------------
            # REPORT
            # ------------------------------------------------

            with tabs[0]:

                report = str(
                    result.get(
                        "report",
                        "",
                    )
                ).strip()

                if report:

                    st.markdown(
                        report
                    )

                else:

                    st.warning(
                        "No research report was returned."
                    )

            # ------------------------------------------------
            # CRITIQUE
            # ------------------------------------------------

            with tabs[1]:

                feedback = str(
                    result.get(
                        "feedback",
                        "",
                    )
                ).strip()

                if feedback:

                    st.markdown(
                        feedback
                    )

                else:

                    st.warning(
                        "No critique was returned."
                    )

            # ------------------------------------------------
            # SEARCH RESULTS
            # ------------------------------------------------

            with tabs[2]:

                search_results = str(
                    result.get(
                        "search_results",
                        "",
                    )
                ).strip()

                if search_results:

                    st.text_area(
                        "Search results",
                        value=search_results,
                        height=450,
                        label_visibility="collapsed",
                    )

                else:

                    st.info(
                        "No search results were returned."
                    )

            # ------------------------------------------------
            # SCRAPED SOURCES
            # ------------------------------------------------

            with tabs[3]:

                scraped_content = str(
                    result.get(
                        "scraped_content",
                        "",
                    )
                ).strip()

                if scraped_content:

                    st.subheader(
                        "Source Content"
                    )

                    st.text_area(
                        "Scraped source",
                        value=scraped_content,
                        height=600,
                        label_visibility="collapsed",
                    )

                else:

                    st.info(
                        "No scraped source content was returned."
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MULTI-AGENT AI RESEARCH SYSTEM"
)

st.caption(
    "SEARCH → READ → WRITE → CRITIQUE"
)

st.caption(
    "LangChain · Groq · Tavily · BeautifulSoup · Streamlit"
)

st.caption(
    "🌐 ENGLISH · 🇮🇳 HINDI · 🎙️ VOICE · 🌤️ LIVE WEATHER"
)