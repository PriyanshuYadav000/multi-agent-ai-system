import json
import re

import streamlit as st
import streamlit.components.v1 as components

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
# SESSION STATE
# ============================================================

if "query" not in st.session_state:
    st.session_state.query = ""

if "result" not in st.session_state:
    st.session_state.result = None


# ============================================================
# HTML HELPER
# ============================================================

def md(
    html_string: str,
) -> None:

    flattened = "\n".join(
        line.strip()
        for line in html_string.strip(
            "\n"
        ).split("\n")
    )

    st.markdown(
        flattened,
        unsafe_allow_html=True,
    )


# ============================================================
# GROQ SPEECH TO TEXT
# ============================================================

def transcribe_audio(
    audio_bytes: bytes,
    language: str,
) -> str:

    client = Groq()

    language_code = (
        "hi"
        if language == "Hindi"
        else "en"
    )

    transcription = (
        client.audio.transcriptions.create(
            file=(
                "recording.webm",
                audio_bytes,
            ),
            model="whisper-large-v3-turbo",
            language=language_code,
            response_format="json",
            temperature=0,
        )
    )

    return transcription.text.strip()


# ============================================================
# BROWSER TEXT TO SPEECH
# ============================================================

def speech_button(
    text: str,
    language: str,
    key: str,
):

    clean_text = re.sub(
        r"https?://\S+",
        "",
        text,
    )

    clean_text = clean_text[:3500]

    speech_language = (
        "hi-IN"
        if language == "Hindi"
        else "en-US"
    )

    encoded_text = json.dumps(
        clean_text
    )

    components.html(
        f"""
        <button
            onclick='speakResponse()'
            style="
                width:100%;
                padding:12px;
                border-radius:12px;
                border:1px solid rgba(99,246,255,0.35);
                background:
                    linear-gradient(
                        90deg,
                        rgba(99,246,255,0.12),
                        rgba(124,92,237,0.12)
                    );
                color:#efffff;
                font-weight:800;
                cursor:pointer;
                font-size:14px;
            "
        >
            🔊 SPEAK RESPONSE
        </button>

        <script>

        function speakResponse() {{

            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(
                    {encoded_text}
                );

            utterance.lang =
                "{speech_language}";

            utterance.rate = 0.95;
            utterance.pitch = 1.0;

            window.speechSynthesis.speak(
                utterance
            );
        }}

        </script>
        """,
        height=55,
    )


# ============================================================
# PHASE DATA
# ============================================================

PHASES = [
    (
        "search",
        "🔎",
        "SEARCH AGENT",
        "WEB DISCOVERY",
    ),
    (
        "reader",
        "📖",
        "READER AGENT",
        "SOURCE EXTRACTION",
    ),
    (
        "writer",
        "✍️",
        "WRITER CHAIN",
        "REPORT GENERATION",
    ),
    (
        "critic",
        "🧠",
        "CRITIC CHAIN",
        "QUALITY EVALUATION",
    ),
]


# ============================================================
# PHASE UI
# ============================================================

def render_pipeline(
    placeholder,
    active_stage=None,
    completed=None,
):

    completed = completed or set()

    cards = []

    for (
        key,
        icon,
        name,
        subtitle,
    ) in PHASES:

        if key in completed:

            css_class = "complete"
            status = "COMPLETE"

        elif key == active_stage:

            css_class = "active"
            status = "RUNNING"

        else:

            css_class = "waiting"
            status = "WAITING"

        cards.append(
            f"""
            <div class="
                phase-card {css_class}
            ">

                <div class="phase-top">
                    <span class="phase-icon">
                        {icon}
                    </span>

                    <span class="phase-number">
                        {key.upper()}
                    </span>
                </div>

                <div class="phase-name">
                    {name}
                </div>

                <div class="phase-subtitle">
                    {subtitle}
                </div>

                <div class="phase-status">
                    <span class="phase-dot"></span>
                    {status}
                </div>

            </div>
            """
        )

    placeholder.markdown(
        f"""
        <div class="phase-grid">
            {"".join(cards)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CALLBACK
# ============================================================

def make_progress_callback(
    placeholder,
):

    completed = set()

    def callback(
        stage,
        status,
    ):

        if status == "complete":

            completed.add(stage)

            render_pipeline(
                placeholder,
                None,
                completed,
            )

        else:

            render_pipeline(
                placeholder,
                stage,
                completed,
            )

    return callback


# ============================================================
# CSS
# ============================================================

md(
    """
    <style>

    * {
        box-sizing: border-box;
    }

    .stApp {

        min-height:100vh;

        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(0,234,255,0.13),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 15%,
                rgba(124,58,237,0.14),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                #02050a 0%,
                #050811 50%,
                #03060c 100%
            );

        color:#f5f7fb;
    }

    .stApp::before {

        content:"";

        position:fixed;

        inset:0;

        background-image:
            linear-gradient(
                rgba(90,240,255,0.025) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(90,240,255,0.025) 1px,
                transparent 1px
            );

        background-size:46px 46px;

        pointer-events:none;

        z-index:0;
    }

    header {
        visibility:hidden;
    }

    footer {
        visibility:hidden;
    }

    #MainMenu {
        visibility:hidden;
    }

    .block-container {

        max-width:1380px;

        padding-top:1rem;
        padding-bottom:4rem;

        position:relative;

        z-index:3;
    }

    /* ========================================================
       HERO
       ======================================================== */

    .hero {

        text-align:center;

        padding:
            2.5rem
            1rem
            2rem;
    }

    .hero-badge {

        display:inline-flex;

        padding:
            0.5rem 1rem;

        border-radius:999px;

        border:
            1px solid
            rgba(99,246,255,0.25);

        background:
            rgba(99,246,255,0.05);

        color:#63f6ff;

        font-family:monospace;

        font-size:0.7rem;

        letter-spacing:1.5px;
    }

    .hero-title {

        margin-top:1rem;

        font-size:
            clamp(
                2.5rem,
                6vw,
                5rem
            );

        font-weight:800;

        line-height:1;

        letter-spacing:-2px;

        background:
            linear-gradient(
                105deg,
                #fff,
                #63f6ff,
                #a78bfa,
                #fff
            );

        -webkit-background-clip:text;

        -webkit-text-fill-color:transparent;
    }

    .hero-subtitle {

        max-width:820px;

        margin:
            1.2rem auto 0;

        color:#909cad;

        line-height:1.8;
    }

    /* ========================================================
       COMMAND PANEL
       ======================================================== */

    .command-panel {

        padding:1.6rem;

        border-radius:24px;

        background:
            linear-gradient(
                145deg,
                rgba(10,17,30,0.92),
                rgba(4,9,17,0.82)
            );

        border:
            1px solid
            rgba(99,246,255,0.16);

        box-shadow:
            0 30px 80px
            rgba(0,0,0,0.35);
    }

    .command-header {

        display:flex;

        justify-content:space-between;

        align-items:center;

        margin-bottom:1.3rem;
    }

    .command-title {

        color:#eafcff;

        font-size:1.05rem;

        font-weight:800;
    }

    .command-meta {

        color:#63f6ff;

        font-family:monospace;

        font-size:0.62rem;
    }

    .query-title {

        color:#63f6ff;

        font-family:monospace;

        font-size:0.72rem;

        letter-spacing:1.7px;

        margin-bottom:0.6rem;
    }

    /* ========================================================
       TEXT INPUT
       ======================================================== */

    .stTextInput > div > div > input {

        min-height:62px;

        background:#080e17 !important;

        color:#ffffff !important;

        border:
            1px solid
            rgba(99,246,255,0.32)
            !important;

        border-radius:15px !important;

        font-size:1.03rem !important;

        padding:
            0.8rem
            1.1rem !important;
    }

    .stTextInput > div > div > input:focus {

        border-color:
            rgba(99,246,255,0.8)
            !important;

        box-shadow:
            0 0 30px
            rgba(99,246,255,0.1)
            !important;
    }

    /* ========================================================
       SELECT
       ======================================================== */

    div[data-baseweb="select"] > div {

        background:#080e17 !important;

        border:
            1px solid
            rgba(255,255,255,0.12)
            !important;

        border-radius:13px !important;
    }

    /* ========================================================
       BUTTON
       ======================================================== */

    .stButton > button {

        width:100%;

        min-height:58px;

        border-radius:14px;

        border:
            1px solid
            rgba(99,246,255,0.4);

        background:
            linear-gradient(
                90deg,
                rgba(99,246,255,0.14),
                rgba(124,92,237,0.14)
            );

        color:#efffff;

        font-weight:800;

        transition:0.25s ease;
    }

    .stButton > button:hover {

        transform:
            translateY(-2px);

        border-color:
            rgba(99,246,255,0.82);

        box-shadow:
            0 0 35px
            rgba(99,246,255,0.12);
    }

    /* ========================================================
       MICROPHONE
       ======================================================== */

    .voice-panel {

        margin-top:1rem;

        padding:1rem;

        border-radius:16px;

        background:
            rgba(99,246,255,0.025);

        border:
            1px dashed
            rgba(99,246,255,0.22);

        text-align:center;

        color:#93a0b3;

        font-size:0.78rem;
    }

    /* ========================================================
       PHASES
       ======================================================== */

    .phase-grid {

        display:grid;

        grid-template-columns:
            repeat(4,1fr);

        gap:14px;

        margin-top:1.4rem;

        margin-bottom:1.8rem;
    }

    .phase-card {

        min-height:175px;

        padding:1.25rem;

        border-radius:20px;

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.045),
                rgba(255,255,255,0.012)
            );

        border:
            1px solid
            rgba(255,255,255,0.08);

        transition:
            all 0.3s ease;

        position:relative;

        overflow:hidden;
    }

    .phase-card.waiting {

        opacity:0.45;
    }

    .phase-card.active {

        opacity:1;

        border-color:
            rgba(99,246,255,0.7);

        box-shadow:
            0 0 45px
            rgba(99,246,255,0.14);

        transform:
            translateY(-5px);
    }

    .phase-card.active::after {

        content:"";

        position:absolute;

        inset:0;

        border-radius:20px;

        box-shadow:
            inset 0 0 35px
            rgba(99,246,255,0.08);

        animation:
            phasePulse 1.5s
            ease-in-out infinite;
    }

    .phase-card.complete {

        opacity:0.95;

        border-color:
            rgba(0,255,170,0.45);

        box-shadow:
            0 0 24px
            rgba(0,255,170,0.07);
    }

    @keyframes phasePulse {

        0%,
        100% {
            opacity:0.35;
        }

        50% {
            opacity:1;
        }
    }

    .phase-top {

        display:flex;

        justify-content:space-between;

        align-items:center;
    }

    .phase-icon {

        font-size:2rem;
    }

    .phase-number {

        color:#46566b;

        font-family:monospace;

        font-size:0.58rem;
    }

    .phase-name {

        margin-top:0.65rem;

        color:#f3f7fb;

        font-size:0.94rem;

        font-weight:800;
    }

    .phase-subtitle {

        margin-top:0.3rem;

        color:#68778c;

        font-family:monospace;

        font-size:0.6rem;

        letter-spacing:0.7px;
    }

    .phase-status {

        display:inline-flex;

        align-items:center;

        gap:6px;

        margin-top:0.9rem;

        padding:
            0.3rem 0.6rem;

        border-radius:999px;

        border:
            1px solid
            rgba(99,246,255,0.13);

        background:
            rgba(99,246,255,0.04);

        color:#63f6ff;

        font-family:monospace;

        font-size:0.57rem;
    }

    .phase-card.complete .phase-status {

        color:#6dffcb;

        border-color:
            rgba(0,255,170,0.2);
    }

    .phase-dot {

        width:5px;

        height:5px;

        border-radius:50%;

        background:#63f6ff;

        box-shadow:
            0 0 9px #63f6ff;
    }

    .phase-card.complete
    .phase-dot {

        background:#00ffaa;

        box-shadow:
            0 0 9px #00ffaa;
    }

    /* ========================================================
       STATUS
       ======================================================== */

    [data-testid="stStatus"] {

        border-radius:18px;

        background:
            rgba(7,12,21,0.84);

        border:
            1px solid
            rgba(99,246,255,0.12);
    }

    /* ========================================================
       OUTPUT
       ======================================================== */

    .output-wrapper {

        margin-top:1rem;

        padding:1.8rem;

        border-radius:22px;

        background:
            rgba(7,12,21,0.78);

        border:
            1px solid
            rgba(255,255,255,0.07);
    }

    .status-pill {

        display:inline-flex;

        padding:
            0.35rem 0.75rem;

        border-radius:999px;

        color:#63f6ff;

        background:
            rgba(99,246,255,0.05);

        border:
            1px solid
            rgba(99,246,255,0.15);

        font-family:monospace;

        font-size:0.62rem;

        letter-spacing:1px;

        margin-bottom:1rem;
    }

    /* ========================================================
       TABS
       ======================================================== */

    .stTabs [data-baseweb="tab-list"] {

        gap:4px;

        padding:4px;

        background:
            rgba(4,8,15,0.76);

        border-radius:16px;
    }

    .stTabs [data-baseweb="tab"] {

        border-radius:10px;

        color:#78869a;

        font-size:0.8rem;
    }

    .stTabs [aria-selected="true"] {

        color:#63f6ff;

        background:
            rgba(99,246,255,0.08);
    }

    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media(max-width:900px) {

        .phase-grid {

            grid-template-columns:
                repeat(2,1fr);
        }
    }

    @media(max-width:600px) {

        .phase-grid {

            grid-template-columns:1fr;
        }

        .command-header {

            flex-direction:column;

            align-items:flex-start;

            gap:7px;
        }
    }

    </style>
    """
)


# ============================================================
# HERO
# ============================================================

md(
    """
    <div class="hero">

        <div class="hero-badge">
            ● AUTONOMOUS MULTI-AGENT RESEARCH
        </div>

        <div class="hero-title">
            Multi-Agent AI Research System
        </div>

        <div class="hero-subtitle">
            Search the live web, read real sources,
            generate structured research, evaluate the result,
            and interact with the AI using English or Hindi voice.
        </div>

    </div>
    """
)


# ============================================================
# COMMAND HEADER
# ============================================================

md(
    """
    <div class="command-panel">

        <div class="command-header">

            <div class="command-title">
                🔎 Research Intelligence Console
            </div>

            <div class="command-meta">
                MULTI_AGENT_PIPELINE :: READY
            </div>

        </div>

        <div class="query-title">
            ENTER YOUR RESEARCH QUERY
        </div>

    </div>
    """
)


# ============================================================
# QUERY INPUT
# ============================================================

topic = st.text_input(
    "Research query",
    value=st.session_state.query,
    placeholder=(
        "Ask anything... "
        "e.g. Latest AI developments in 2026"
    ),
    label_visibility="collapsed",
    key="query",
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
        index=0,
    )


with button_col:

    run_button = st.button(
        "🚀  START RESEARCH",
        type="primary",
    )


# ============================================================
# VOICE
# ============================================================

md(
    """
    <div class="voice-panel">
        🎙️ Speak your question → AI transcribes it →
        Research / Weather → response in your selected language.
    </div>
    """
)


audio = mic_recorder(
    start_prompt="🎙️ START SPEAKING",
    stop_prompt="⏹️ STOP RECORDING",
    just_once=True,
    use_container_width=True,
    format="webm",
    key="research_mic",
)


if audio:

    try:

        with st.spinner(
            "Transcribing your voice..."
        ):

            transcript = transcribe_audio(
                audio["bytes"],
                language,
            )

        if transcript:

            st.session_state.query = (
                transcript
            )

            st.success(
                f"Voice query: {transcript}"
            )

            st.rerun()

    except Exception as exc:

        st.error(
            f"Voice transcription failed: {exc}"
        )


# ============================================================
# RUN PIPELINE
# ============================================================

if run_button:

    if not topic.strip():

        st.warning(
            "Please enter a query or use the microphone."
        )

        st.stop()

    progress_placeholder = st.empty()

    render_pipeline(
        progress_placeholder
    )

    try:

        with st.status(
            "AI pipeline is running...",
            expanded=True,
        ) as status:

            callback = (
                make_progress_callback(
                    progress_placeholder
                )
            )

            status.write(
                "Initializing AI agents..."
            )

            result = run_research_pipeline(
                topic=topic,
                language=language,
                progress_callback=callback,
            )

            status.write(
                "AI response generated."
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

        st.stop()


# ============================================================
# DISPLAY RESULT
# ============================================================

result = st.session_state.result


if result:

    st.markdown(
        "---"
    )

    # ========================================================
    # WEATHER
    # ========================================================

    if result.get("mode") == "weather":

        md(
            """
            <div class="output-wrapper">
                <div class="status-pill">
                    ● LIVE WEATHER
                </div>
            """
        )

        st.markdown(
            "## 🌤️ Current Weather"
        )

        st.markdown(
            result["weather"]
        )

        speech_button(
            result["weather"],
            result["language"],
            "weather_speech",
        )

        md(
            """
            </div>
            """
        )

    # ========================================================
    # RESEARCH
    # ========================================================

    else:

        md(
            """
            <div class="output-wrapper">
                <div class="status-pill">
                    ● GENERATED RESEARCH
                </div>
            """
        )

        tabs = st.tabs(
            [
                "📄 Research Report",
                "🧠 Critique",
                "🔎 Search Results",
                "📖 Scraped Sources",
            ]
        )

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        with tabs[0]:

            st.markdown(
                result["report"]
            )

            speech_button(
                result["report"],
                result["language"],
                "report_speech",
            )

        # ----------------------------------------------------
        # CRITIQUE
        # ----------------------------------------------------

        with tabs[1]:

            st.markdown(
                result["feedback"]
            )

            speech_button(
                result["feedback"],
                result["language"],
                "critique_speech",
            )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        with tabs[2]:

            st.markdown(
                result["search_results"]
            )

        # ----------------------------------------------------
        # SCRAPED
        # ----------------------------------------------------

        with tabs[3]:

            st.markdown(
                result["scraped_content"]
            )

        md(
            """
            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

md(
    """
    <div style="
        text-align:center;
        margin-top:4rem;
        padding:2rem;
        color:#526074;
        font-family:monospace;
        font-size:0.68rem;
        line-height:1.9;
    ">

        MULTI-AGENT AI RESEARCH SYSTEM

        <br>

        SEARCH → READ → WRITE → CRITIQUE

        <br>

        LangChain · Groq · Tavily · BeautifulSoup · Streamlit

        <br>

        🌐 ENGLISH · 🇮🇳 HINDI · 🎙️ VOICE · 🌤️ LIVE WEATHER

    </div>
    """
)