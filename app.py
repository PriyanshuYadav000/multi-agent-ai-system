import streamlit as st

from pipeline import run_research_pipeline


# ============================================================
# HTML HELPER
# ============================================================

def md(html_string: str) -> None:
    """
    Safely render HTML through Streamlit Markdown.
    Removes indentation so HTML is not displayed as code.
    """
    flattened = "\n".join(
        line.strip()
        for line in html_string.strip("\n").split("\n")
    )

    st.markdown(
        flattened,
        unsafe_allow_html=True
    )


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
# CUSTOM CSS
# ============================================================

md(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    * {
        box-sizing: border-box;
    }

    html {
        scroll-behavior: smooth;
    }

    body {
        margin: 0;
        padding: 0;
    }

    .stApp {
        min-height: 100vh;

        background:
            radial-gradient(
                circle at 12% 12%,
                rgba(0, 229, 255, 0.11),
                transparent 28%
            ),
            radial-gradient(
                circle at 88% 18%,
                rgba(139, 92, 246, 0.13),
                transparent 30%
            ),
            radial-gradient(
                circle at 55% 85%,
                rgba(0, 255, 170, 0.045),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                #02050a 0%,
                #050811 45%,
                #03060c 100%
            );

        color: #f5f7fb;

        overflow-x: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1320px;

        padding-top: 1.2rem;
        padding-bottom: 4rem;

        position: relative;
        z-index: 5;
    }


    /* ========================================================
       ANIMATED BACKGROUND GRID
       ======================================================== */

    .stApp::before {
        content: "";

        position: fixed;

        inset: 0;

        background-image:
            linear-gradient(
                rgba(90, 240, 255, 0.032) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(90, 240, 255, 0.032) 1px,
                transparent 1px
            );

        background-size: 46px 46px;

        -webkit-mask-image:
            radial-gradient(
                ellipse 90% 70% at 50% 15%,
                black 15%,
                transparent 88%
            );

        mask-image:
            radial-gradient(
                ellipse 90% 70% at 50% 15%,
                black 15%,
                transparent 88%
            );

        pointer-events: none;

        z-index: 0;

        animation:
            gridDrift 32s linear infinite;
    }

    @keyframes gridDrift {

        0% {
            transform: translate3d(0, 0, 0);
        }

        100% {
            transform: translate3d(46px, 46px, 0);
        }

    }


    /* ========================================================
       AMBIENT LIGHT
       ======================================================== */

    .ambient {
        position: fixed;

        border-radius: 50%;

        pointer-events: none;

        z-index: 0;

        filter: blur(90px);

        opacity: 0.18;
    }

    .ambient-a {
        width: 260px;
        height: 260px;

        left: -50px;
        top: 90px;

        background: #00eaff;

        animation:
            ambientA 11s ease-in-out infinite;
    }

    .ambient-b {
        width: 300px;
        height: 300px;

        right: -70px;
        top: 320px;

        background: #7c3aed;

        animation:
            ambientB 14s ease-in-out infinite;
    }

    .ambient-c {
        width: 220px;
        height: 220px;

        left: 42%;
        bottom: 50px;

        background: #00ffaa;

        animation:
            ambientC 18s ease-in-out infinite;
    }

    @keyframes ambientA {

        0%,
        100% {
            transform: translate(0, 0) scale(1);
        }

        50% {
            transform: translate(55px, 25px) scale(1.15);
        }

    }

    @keyframes ambientB {

        0%,
        100% {
            transform: translate(0, 0) scale(1);
        }

        50% {
            transform: translate(-45px, 40px) scale(1.12);
        }

    }

    @keyframes ambientC {

        0%,
        100% {
            transform: translate(0, 0) scale(1);
        }

        50% {
            transform: translate(30px, -35px) scale(1.1);
        }

    }


    /* ========================================================
       SCAN LINE
       ======================================================== */

    .scan-line {
        position: fixed;

        top: 0;
        left: 0;

        width: 100%;
        height: 1px;

        background:
            linear-gradient(
                90deg,
                transparent,
                #63f6ff,
                #a78bfa,
                transparent
            );

        box-shadow:
            0 0 18px rgba(99,246,255,0.8);

        opacity: 0.5;

        z-index: 15;

        pointer-events: none;

        animation:
            scanMove 8s linear infinite;
    }

    @keyframes scanMove {

        0% {
            top: 0%;
            opacity: 0;
        }

        8% {
            opacity: 0.55;
        }

        50% {
            opacity: 0.3;
        }

        92% {
            opacity: 0.55;
        }

        100% {
            top: 100%;
            opacity: 0;
        }

    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        position: relative;

        padding:
            3rem
            1rem
            2rem;

        text-align: center;

        z-index: 3;
    }

    .hero-badge {
        display: inline-flex;

        align-items: center;

        gap: 0.55rem;

        padding:
            0.45rem
            1rem;

        border-radius: 999px;

        background:
            rgba(99,246,255,0.055);

        border:
            1px solid rgba(99,246,255,0.24);

        color:
            #63f6ff;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.7rem;

        font-weight:
            600;

        letter-spacing:
            1.8px;

        text-transform:
            uppercase;

        box-shadow:
            0 0 30px rgba(99,246,255,0.06);

        backdrop-filter:
            blur(16px);
    }

    .pulse-dot {
        width: 7px;
        height: 7px;

        display: inline-block;

        border-radius: 50%;

        background: #63f6ff;

        box-shadow:
            0 0 8px #63f6ff,
            0 0 18px #63f6ff;

        animation:
            pulseDot 1.7s ease-in-out infinite;
    }

    @keyframes pulseDot {

        0%,
        100% {
            opacity: 1;
            transform: scale(1);
        }

        50% {
            opacity: 0.35;
            transform: scale(0.72);
        }

    }

    .hero-title {
        margin-top: 1.2rem;

        font-size:
            clamp(
                2.7rem,
                7vw,
                5.2rem
            );

        font-weight:
            800;

        line-height:
            0.98;

        letter-spacing:
            -3px;

        background:
            linear-gradient(
                105deg,
                #ffffff 5%,
                #63f6ff 34%,
                #7c8cff 50%,
                #a78bfa 62%,
                #ffffff 92%
            );

        background-size:
            260% auto;

        -webkit-background-clip:
            text;

        -webkit-text-fill-color:
            transparent;

        animation:
            heroShimmer 8s linear infinite;
    }

    @keyframes heroShimmer {

        from {
            background-position: 0% 50%;
        }

        to {
            background-position: 260% 50%;
        }

    }

    .hero-subtitle {
        max-width:
            780px;

        margin:
            1.2rem auto 0;

        color:
            #929dad;

        font-size:
            1rem;

        line-height:
            1.85;
    }


    /* ========================================================
       3D AI CORE
       ======================================================== */

    .ai-core-scene {
        position: relative;

        width: 100%;

        height: 410px;

        margin:
            0.5rem auto
            1.2rem;

        display: flex;

        justify-content:
            center;

        align-items:
            center;

        perspective:
            1100px;

        z-index:
            2;

        overflow:
            hidden;
    }

    .ai-core {
        position: relative;

        width: 190px;
        height: 190px;

        transform-style:
            preserve-3d;

        animation:
            coreFloat 5s ease-in-out infinite;
    }

    @keyframes coreFloat {

        0%,
        100% {
            transform:
                translateY(0px)
                rotateX(2deg)
                rotateY(0deg);
        }

        50% {
            transform:
                translateY(-12px)
                rotateX(7deg)
                rotateY(12deg);
        }

    }

    .core-shell {
        position:
            absolute;

        inset:
            8px;

        border-radius:
            50%;

        background:
            radial-gradient(
                circle at 32% 28%,
                #d9ffff 0%,
                #7cecff 10%,
                #14bfe5 26%,
                #173c70 55%,
                #070d22 79%
            );

        border:
            1px solid rgba(166,250,255,0.7);

        box-shadow:
            inset -18px -18px 40px rgba(0,0,0,0.45),
            inset 18px 18px 30px rgba(255,255,255,0.14),
            0 0 35px rgba(99,246,255,0.4),
            0 0 95px rgba(99,246,255,0.16);

        transform:
            translateZ(30px);
    }

    .core-inner {
        position:
            absolute;

        inset:
            36px;

        border-radius:
            50%;

        background:
            radial-gradient(
                circle,
                #ffffff 0%,
                #63f6ff 16%,
                #6e5dfc 48%,
                #0b1130 100%
            );

        box-shadow:
            0 0 22px rgba(99,246,255,0.75),
            inset 0 0 20px rgba(255,255,255,0.3);

        transform:
            translateZ(48px);

        animation:
            corePulse 2.3s ease-in-out infinite;
    }

    @keyframes corePulse {

        0%,
        100% {
            transform:
                translateZ(48px)
                scale(1);
        }

        50% {
            transform:
                translateZ(48px)
                scale(1.08);
        }

    }

    .ring {
        position:
            absolute;

        inset:
            -18px;

        border:
            1px solid rgba(99,246,255,0.42);

        border-radius:
            50%;

        transform-style:
            preserve-3d;

        pointer-events:
            none;
    }

    .ring-one {
        transform:
            rotateX(70deg)
            rotateZ(15deg);

        animation:
            ringOne 9s linear infinite;
    }

    .ring-two {
        inset:
            -34px;

        border-color:
            rgba(167,139,250,0.45);

        transform:
            rotateY(70deg)
            rotateZ(24deg);

        animation:
            ringTwo 11s linear infinite reverse;
    }

    .ring-three {
        inset:
            -51px;

        border-color:
            rgba(99,246,255,0.2);

        transform:
            rotateX(64deg)
            rotateY(20deg);

        animation:
            ringThree 14s linear infinite;
    }

    @keyframes ringOne {

        from {
            transform:
                rotateX(70deg)
                rotateZ(0deg);
        }

        to {
            transform:
                rotateX(70deg)
                rotateZ(360deg);
        }

    }

    @keyframes ringTwo {

        from {
            transform:
                rotateY(70deg)
                rotateZ(0deg);
        }

        to {
            transform:
                rotateY(70deg)
                rotateZ(360deg);
        }

    }

    @keyframes ringThree {

        from {
            transform:
                rotateX(64deg)
                rotateY(20deg)
                rotateZ(0deg);
        }

        to {
            transform:
                rotateX(64deg)
                rotateY(20deg)
                rotateZ(360deg);
        }

    }


    /* ========================================================
       FLOATING NODES
       ======================================================== */

    .floating-node {
        position:
            absolute;

        padding:
            0.55rem
            0.85rem;

        border-radius:
            12px;

        background:
            rgba(8,14,28,0.72);

        border:
            1px solid rgba(99,246,255,0.2);

        color:
            #a8f9ff;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.65rem;

        backdrop-filter:
            blur(14px);

        box-shadow:
            0 10px 30px rgba(0,0,0,0.25),
            0 0 22px rgba(99,246,255,0.06);

        animation:
            nodeFloat 5s ease-in-out infinite;
    }

    .node-one {
        left:
            18%;

        top:
            32%;

        animation-delay:
            -1s;
    }

    .node-two {
        right:
            17%;

        top:
            22%;

        animation-delay:
            -2.2s;
    }

    .node-three {
        left:
            25%;

        bottom:
            16%;

        animation-delay:
            -3.5s;
    }

    .node-four {
        right:
            25%;

        bottom:
            14%;

        animation-delay:
            -4s;
    }

    @keyframes nodeFloat {

        0%,
        100% {
            transform:
                translateY(0)
                rotateX(0deg);
        }

        50% {
            transform:
                translateY(-12px)
                rotateX(5deg);
        }

    }


    /* ========================================================
       PIPELINE
       ======================================================== */

    .pipeline-panel {
        margin-top:
            0.5rem;

        padding:
            1.3rem;

        border-radius:
            24px;

        background:
            linear-gradient(
                145deg,
                rgba(10,17,30,0.78),
                rgba(4,9,17,0.68)
            );

        border:
            1px solid rgba(99,246,255,0.1);

        box-shadow:
            0 30px 80px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.025);

        backdrop-filter:
            blur(18px);
    }

    .pipeline-title {
        color:
            #7befff;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.72rem;

        letter-spacing:
            1.8px;

        font-weight:
            700;

        margin:
            0.1rem
            0
            1rem;
    }

    .pipeline-title::before {
        content:
            "● ";

        color:
            #63f6ff;

        text-shadow:
            0 0 10px #63f6ff;
    }

    .agent-wrapper {
        position:
            relative;

        min-height:
            175px;

        padding:
            1.2rem
            0.8rem;

        text-align:
            center;

        border-radius:
            20px;

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.012)
            );

        border:
            1px solid rgba(255,255,255,0.08);

        backdrop-filter:
            blur(14px);

        overflow:
            hidden;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.035),
            0 15px 45px rgba(0,0,0,0.2);

        transition:
            transform 0.3s ease,
            border-color 0.3s ease,
            box-shadow 0.3s ease;
    }

    .agent-wrapper::before {
        content:
            "";

        position:
            absolute;

        width:
            120px;

        height:
            120px;

        top:
            -60px;

        left:
            50%;

        transform:
            translateX(-50%);

        background:
            radial-gradient(
                circle,
                rgba(99,246,255,0.14),
                transparent 70%
            );

        pointer-events:
            none;
    }

    .agent-wrapper:hover {
        transform:
            translateY(-8px)
            perspective(900px)
            rotateX(2deg);

        border-color:
            rgba(99,246,255,0.28);

        box-shadow:
            0 22px 55px rgba(0,0,0,0.3),
            0 0 35px rgba(99,246,255,0.07);
    }

    .agent-icon {
        position:
            relative;

        font-size:
            2rem;

        margin:
            0.15rem
            0
            0.6rem;

        filter:
            drop-shadow(
                0 0 11px
                rgba(99,246,255,0.55)
            );
    }

    .agent-name {
        color:
            #f4f7fb;

        font-weight:
            700;

        font-size:
            0.93rem;
    }

    .agent-type {
        color:
            #69778b;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.63rem;

        letter-spacing:
            0.8px;

        margin-top:
            0.35rem;
    }

    .agent-status {
        display:
            inline-flex;

        align-items:
            center;

        gap:
            0.35rem;

        margin-top:
            0.75rem;

        padding:
            0.3rem
            0.65rem;

        border-radius:
            999px;

        border:
            1px solid rgba(99,246,255,0.12);

        background:
            rgba(99,246,255,0.045);

        color:
            #63f6ff;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.58rem;

        letter-spacing:
            0.7px;
    }

    .status-light {
        width:
            5px;

        height:
            5px;

        border-radius:
            50%;

        background:
            #63f6ff;

        box-shadow:
            0 0 7px #63f6ff;

        animation:
            pulseDot 1.7s ease-in-out infinite;
    }

    .flow-arrow {
        height:
            100%;

        min-height:
            175px;

        display:
            flex;

        align-items:
            center;

        justify-content:
            center;

        position:
            relative;
    }

    .flow-arrow span {
        color:
            #4c6279;

        font-size:
            1.7rem;

        position:
            relative;

        z-index:
            2;
    }

    .flow-arrow::before {
        content:
            "";

        position:
            absolute;

        left:
            0;

        right:
            0;

        height:
            2px;

        background:
            rgba(99,246,255,0.08);
    }

    .flow-arrow::after {
        content:
            "";

        position:
            absolute;

        left:
            -20%;

        width:
            45%;

        height:
            2px;

        background:
            linear-gradient(
                90deg,
                transparent,
                #63f6ff,
                transparent
            );

        box-shadow:
            0 0 10px rgba(99,246,255,0.8);

        animation:
            flowArrow 1.7s ease-in-out infinite;
    }

    @keyframes flowArrow {

        from {
            left:
                -45%;
        }

        to {
            left:
                100%;
        }

    }


    /* ========================================================
       RESEARCH COMMAND
       ======================================================== */

    .section-label {
        margin:
            2rem
            0
            0.8rem;

        color:
            #63f6ff;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.7rem;

        font-weight:
            700;

        letter-spacing:
            2px;

        text-transform:
            uppercase;
    }

    .section-label::before {
        content:
            "/// ";

        color:
            #46576b;
    }

    .command-panel {
        padding:
            1.4rem;

        border-radius:
            22px;

        background:
            linear-gradient(
                145deg,
                rgba(8,15,26,0.84),
                rgba(4,9,17,0.74)
            );

        border:
            1px solid rgba(99,246,255,0.12);

        box-shadow:
            0 25px 70px rgba(0,0,0,0.24);

        backdrop-filter:
            blur(18px);

        margin-bottom:
            0.8rem;
    }

    .command-topline {
        display:
            flex;

        align-items:
            center;

        justify-content:
            space-between;

        margin-bottom:
            1rem;
    }

    .command-title {
        color:
            #eafcff;

        font-size:
            0.95rem;

        font-weight:
            700;
    }

    .command-meta {
        color:
            #5e6d81;

        font-size:
            0.62rem;

        font-family:
            "JetBrains Mono",
            monospace;
    }


    /* ========================================================
       TEXT INPUT
       ======================================================== */

    .stTextInput > div > div > input {
        min-height:
            54px;

        background:
            #080e17;

        color:
            #f4f7fb;

        border:
            1px solid rgba(255,255,255,0.09);

        border-radius:
            13px;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.82rem;

        padding:
            0.75rem
            1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color:
            rgba(99,246,255,0.55);

        box-shadow:
            0 0 0 1px rgba(99,246,255,0.12),
            0 0 30px rgba(99,246,255,0.07);
    }

    .stTextInput > div > div > input::placeholder {
        color:
            #4e5c6f;
    }


    /* ========================================================
       BUTTON
       ======================================================== */

    .stButton > button {
        width:
            100%;

        min-height:
            54px;

        border-radius:
            13px;

        border:
            1px solid rgba(99,246,255,0.35);

        background:
            linear-gradient(
                90deg,
                rgba(99,246,255,0.12),
                rgba(124,92,246,0.12)
            );

        color:
            #efffff;

        font-weight:
            800;

        letter-spacing:
            0.7px;

        box-shadow:
            0 10px 30px rgba(0,0,0,0.18);

        transition:
            all 0.25s ease;
    }

    .stButton > button:hover {
        border-color:
            rgba(99,246,255,0.75);

        background:
            linear-gradient(
                90deg,
                rgba(99,246,255,0.2),
                rgba(124,92,246,0.18)
            );

        box-shadow:
            0 0 32px rgba(99,246,255,0.13);

        transform:
            translateY(-2px);
    }


    /* ========================================================
       STATUS
       ======================================================== */

    [data-testid="stStatus"] {
        margin-top:
            1.2rem;

        border-radius:
            18px;

        background:
            rgba(7,12,21,0.82);

        border:
            1px solid rgba(99,246,255,0.12);

        box-shadow:
            0 22px 60px rgba(0,0,0,0.28);
    }


    /* ========================================================
       TABS
       ======================================================== */

    .stTabs [data-baseweb="tab-list"] {
        gap:
            0.35rem;

        padding:
            0.35rem;

        background:
            rgba(4,8,15,0.74);

        border:
            1px solid rgba(255,255,255,0.06);

        border-radius:
            16px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius:
            11px;

        color:
            #76859a;

        font-size:
            0.78rem;
    }

    .stTabs [aria-selected="true"] {
        color:
            #63f6ff;

        background:
            linear-gradient(
                90deg,
                rgba(99,246,255,0.08),
                rgba(124,92,246,0.08)
            );
    }


    /* ========================================================
       OUTPUT
       ======================================================== */

    .output-wrapper {
        padding:
            1.8rem;

        margin-top:
            1rem;

        border-radius:
            22px;

        background:
            rgba(7,12,21,0.75);

        border:
            1px solid rgba(255,255,255,0.07);

        box-shadow:
            0 20px 55px rgba(0,0,0,0.22);
    }

    .critic-wrapper {
        padding:
            1.8rem;

        margin-top:
            1rem;

        border-radius:
            22px;

        background:
            linear-gradient(
                145deg,
                rgba(132,93,245,0.09),
                rgba(7,12,21,0.78)
            );

        border:
            1px solid rgba(167,139,250,0.18);
    }

    .status-pill {
        display:
            inline-flex;

        align-items:
            center;

        gap:
            0.45rem;

        margin-bottom:
            0.8rem;

        padding:
            0.35rem
            0.75rem;

        border-radius:
            999px;

        background:
            rgba(99,246,255,0.05);

        border:
            1px solid rgba(99,246,255,0.16);

        color:
            #63f6ff;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.63rem;

        letter-spacing:
            1px;
    }

    .output-wrapper h1,
    .output-wrapper h2,
    .output-wrapper h3 {
        color:
            #f4f7fb;
    }

    .output-wrapper a {
        color:
            #63f6ff;
    }

    .critic-wrapper strong {
        color:
            #e9dfff;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        margin-top:
            4rem;

        padding:
            2rem 0
            0;

        text-align:
            center;

        color:
            #4f5c6e;

        font-family:
            "JetBrains Mono",
            monospace;

        font-size:
            0.68rem;

        line-height:
            1.9;

        letter-spacing:
            0.5px;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 1000px) {

        .ai-core-scene {
            height:
                330px;
        }

        .floating-node {
            display:
                none;
        }

    }

    @media (max-width: 760px) {

        .hero {
            padding-top:
                2rem;
        }

        .hero-title {
            letter-spacing:
                -1.5px;
        }

        .ai-core {
            transform:
                scale(0.82);
        }

        .ai-core-scene {
            height:
                280px;
        }

        .flow-arrow {
            min-height:
                30px;
        }

        .flow-arrow::before,
        .flow-arrow::after {
            display:
                none;
        }

        .flow-arrow span {
            transform:
                rotate(90deg);
        }

        .command-topline {
            flex-direction:
                column;

            align-items:
                flex-start;

            gap:
                0.4rem;
        }

    }

    </style>

    <div class="ambient ambient-a"></div>
    <div class="ambient ambient-b"></div>
    <div class="ambient ambient-c"></div>

    <div class="scan-line"></div>
    """
)


# ============================================================
# HERO
# ============================================================

md(
    """
    <div class="hero">

        <div class="hero-badge">
            <span class="pulse-dot"></span>
            Autonomous Multi-Agent Research
        </div>

        <div class="hero-title">
            Multi-Agent AI Research System
        </div>

        <div class="hero-subtitle">
            A collaborative AI research pipeline that searches the web,
            extracts source knowledge, generates a structured report,
            and automatically evaluates the final result.
        </div>

    </div>
    """
)


# ============================================================
# 3D AI CORE
# ============================================================

md(
    """
    <div class="ai-core-scene">

        <div class="floating-node node-one">
            SEARCH
        </div>

        <div class="floating-node node-two">
            READ
        </div>

        <div class="floating-node node-three">
            WRITE
        </div>

        <div class="floating-node node-four">
            CRITIQUE
        </div>

        <div class="ai-core">

            <div class="ring ring-one"></div>

            <div class="ring ring-two"></div>

            <div class="ring ring-three"></div>

            <div class="core-shell"></div>

            <div class="core-inner"></div>

        </div>

    </div>
    """
)


# ============================================================
# PIPELINE
# ============================================================

md(
    '<div class="pipeline-panel">'
)

md(
    '<div class="pipeline-title">RESEARCH PIPELINE</div>'
)


agent_columns = st.columns(
    [
        1,
        0.12,
        1,
        0.12,
        1,
        0.12,
        1
    ]
)


# ============================================================
# SEARCH AGENT
# ============================================================

with agent_columns[0]:

    md(
        """
        <div class="agent-wrapper">

            <div class="agent-icon">
                🔎
            </div>

            <div class="agent-name">
                Search Agent
            </div>

            <div class="agent-type">
                WEB_DISCOVERY
            </div>

            <div class="agent-status">
                <span class="status-light"></span>
                TAVILY
            </div>

        </div>
        """
    )


# ============================================================
# ARROW
# ============================================================

with agent_columns[1]:

    md(
        """
        <div class="flow-arrow">
            <span>→</span>
        </div>
        """
    )


# ============================================================
# READER AGENT
# ============================================================

with agent_columns[2]:

    md(
        """
        <div class="agent-wrapper">

            <div class="agent-icon">
                📖
            </div>

            <div class="agent-name">
                Reader Agent
            </div>

            <div class="agent-type">
                SOURCE_EXTRACTION
            </div>

            <div class="agent-status">
                <span class="status-light"></span>
                BEAUTIFULSOUP
            </div>

        </div>
        """
    )


# ============================================================
# ARROW
# ============================================================

with agent_columns[3]:

    md(
        """
        <div class="flow-arrow">
            <span>→</span>
        </div>
        """
    )


# ============================================================
# WRITER CHAIN
# ============================================================

with agent_columns[4]:

    md(
        """
        <div class="agent-wrapper">

            <div class="agent-icon">
                ✍️
            </div>

            <div class="agent-name">
                Writer Chain
            </div>

            <div class="agent-type">
                REPORT_GENERATION
            </div>

            <div class="agent-status">
                <span class="status-light"></span>
                GROQ / LLM
            </div>

        </div>
        """
    )


# ============================================================
# ARROW
# ============================================================

with agent_columns[5]:

    md(
        """
        <div class="flow-arrow">
            <span>→</span>
        </div>
        """
    )


# ============================================================
# CRITIC CHAIN
# ============================================================

with agent_columns[6]:

    md(
        """
        <div class="agent-wrapper">

            <div class="agent-icon">
                🧠
            </div>

            <div class="agent-name">
                Critic Chain
            </div>

            <div class="agent-type">
                QUALITY_EVALUATION
            </div>

            <div class="agent-status">
                <span class="status-light"></span>
                LLM REVIEW
            </div>

        </div>
        """
    )


md(
    "</div>"
)


# ============================================================
# RESEARCH COMMAND
# ============================================================

md(
    '<div class="section-label">Research Command</div>'
)

md(
    """
    <div class="command-panel">

        <div class="command-topline">

            <div class="command-title">
                Research Intelligence Console
            </div>

            <div class="command-meta">
                MULTI_AGENT_PIPELINE :: READY
            </div>

        </div>

    </div>
    """
)


topic = st.text_input(
    "Research topic",
    placeholder=(
        "e.g. Impact of AI on software engineering in 2026"
    ),
    label_visibility="collapsed",
)


run_button = st.button(
    "🚀  START RESEARCH",
    type="primary",
)


# ============================================================
# EXECUTION
# ============================================================

if run_button:

    if not topic.strip():

        st.warning(
            "Please enter a research topic."
        )

    else:

        try:

            with st.status(
                "Executing multi-agent research pipeline...",
                expanded=True,
            ) as status:

                status.write(
                    "🔎 Search Agent is researching the web..."
                )

                result = run_research_pipeline(topic)

                status.write(
                    "📖 Reader Agent completed source extraction."
                )

                status.write(
                    "✍️ Writer Chain generated the research report."
                )

                status.write(
                    "🧠 Critic Chain evaluated the report."
                )

                status.update(
                    label=(
                        "Research completed successfully."
                    ),
                    state="complete",
                    expanded=False,
                )

        except Exception as e:

            st.error(
                f"Research pipeline failed: {e}"
            )

            st.stop()


        # ====================================================
        # OUTPUT
        # ====================================================

        md(
            '<div class="section-label">Research Output</div>'
        )


        tabs = st.tabs(
            [
                "📄 Research Report",
                "🧠 Critique",
                "🔎 Search Results",
                "📖 Scraped Sources",
            ]
        )


        # ====================================================
        # REPORT
        # ====================================================

        with tabs[0]:

            md(
                """
                <div class="output-wrapper">
                <div class="status-pill">
                ● GENERATED REPORT
                </div>
                """
            )

            st.markdown(
                result["report"]
            )

            md(
                "</div>"
            )


        # ====================================================
        # CRITIQUE
        # ====================================================

        with tabs[1]:

            md(
                """
                <div class="critic-wrapper">
                <div class="status-pill">
                ● AI QUALITY REVIEW
                </div>
                """
            )

            # IMPORTANT:
            # pipeline.py stores the critic output as "feedback".
            st.markdown(
                result["feedback"]
            )

            md(
                "</div>"
            )


        # ====================================================
        # SEARCH RESULTS
        # ====================================================

        with tabs[2]:

            md(
                """
                <div class="output-wrapper">
                <div class="status-pill">
                ● WEB RESEARCH
                </div>
                """
            )

            st.markdown(
                result["search_results"]
            )

            md(
                "</div>"
            )


        # ====================================================
        # SCRAPED SOURCES
        # ====================================================

        with tabs[3]:

            md(
                """
                <div class="output-wrapper">
                <div class="status-pill">
                ● SOURCE EXTRACTION
                </div>
                """
            )

            # IMPORTANT:
            # pipeline.py stores reader output as "scraped_content".
            st.markdown(
                result["scraped_content"]
            )

            md(
                "</div>"
            )


# ============================================================
# FOOTER
# ============================================================

md(
    """
    <div class="footer">

        MULTI-AGENT AI RESEARCH SYSTEM

        <br>

        SEARCH → READ → WRITE → CRITIQUE

        <br>

        LangChain · Groq · Tavily · BeautifulSoup · Streamlit

    </div>
    """
)