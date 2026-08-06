import os
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from Pipeline import run_research_pipeline


load_dotenv()


st.set_page_config(
    page_title="Multi-Agent Research Studio",
    page_icon="search",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
    }
    .status-box {
        border: 1px solid rgba(49, 51, 63, 0.16);
        border-radius: 8px;
        padding: 0.85rem 1rem;
        background: rgba(248, 250, 252, 0.72);
        margin-bottom: 0.75rem;
    }
    .small-muted {
        color: #64748b;
        font-size: 0.9rem;
    }
</style>
"""


def has_required_keys() -> tuple[bool, list[str]]:
    required = ["HUGGINGFACEHUB_API_TOKEN", "TAVILY_API_KEY"]
    missing = [key for key in required if not os.getenv(key)]
    return len(missing) == 0, missing


def initialize_state() -> None:
    defaults = {
        "last_topic": "",
        "last_result": None,
        "run_started_at": None,
        "run_duration": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Research Setup")
        ready, missing = has_required_keys()

        if ready:
            st.success("API keys loaded")
        else:
            st.error("Missing API keys")
            st.caption(", ".join(missing))

        st.divider()
        st.markdown("**Agent Flow**")
        st.caption("Search agent")
        st.caption("Reader agent")
        st.caption("Writer chain")
        st.caption("Critic chain")

        st.divider()
        st.markdown("**Tips**")
        st.caption("Use a specific topic, timeframe, company, technology, or policy area for sharper results.")


def run_pipeline(topic: str) -> None:
    st.session_state.last_topic = topic
    st.session_state.run_started_at = datetime.now()

    progress = st.progress(0)
    status = st.empty()

    steps = [
        (10, "Preparing agents"),
        (30, "Searching reliable sources"),
        (55, "Reading the most relevant source"),
        (78, "Writing the report"),
        (92, "Reviewing quality"),
    ]

    for percent, label in steps:
        progress.progress(percent)
        status.info(label)
        time.sleep(0.25)

    start = time.perf_counter()
    result = run_research_pipeline(topic)
    duration = time.perf_counter() - start

    progress.progress(100)
    status.success("Research complete")
    st.session_state.last_result = result
    st.session_state.run_duration = duration


def render_result(result: dict) -> None:
    report = result.get("report", "")
    feedback = result.get("feedback", "")
    search_results = result.get("search_results", "")
    scraped_content = result.get("scraped_content", "")
    urls = result.get("urls", [])

    metric_cols = st.columns(3)
    metric_cols[0].metric("Topic", st.session_state.last_topic[:34] or "N/A")
    metric_cols[1].metric("Sections", "4")
    metric_cols[2].metric("Runtime", f"{st.session_state.run_duration:.1f}s" if st.session_state.run_duration else "N/A")

    st.divider()

    report_tab, feedback_tab, sources_tab, raw_tab = st.tabs(
        ["Report", "Critic Feedback", "Search Results", "Scraped Content"]
    )

    with report_tab:
        st.subheader("Research Report")
        st.markdown(report or "_No report generated yet._")
        st.download_button(
            "Download report",
            data=report,
            file_name=f"{st.session_state.last_topic.replace(' ', '_')[:40]}_report.md",
            mime="text/markdown",
            disabled=not bool(report),
        )

    with feedback_tab:
        st.subheader("Quality Review")
        st.markdown(feedback or "_No feedback generated yet._")

    with sources_tab:
        st.subheader("Search Results")
        if urls:
            st.markdown("**Fetched URLs**")
            for url in urls:
                st.markdown(f"- {url}")
        st.text_area("Raw search output", search_results, height=320, label_visibility="collapsed")

    with raw_tab:
        st.subheader("Scraped Source Content")
        st.text_area("Raw scraped content", scraped_content, height=420, label_visibility="collapsed")


def main() -> None:
    initialize_state()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    render_sidebar()

    st.title("Multi-Agent Research Studio")
    st.caption("Search, read, write, and critique a research report with your LangChain agent pipeline.")

    with st.container():
        topic = st.text_input(
            "Research topic",
            placeholder="Example: latest enterprise AI agent orchestration trends in 2026",
        )

        action_cols = st.columns([1, 1, 4])
        run_clicked = action_cols[0].button("Run research", type="primary", use_container_width=True)
        clear_clicked = action_cols[1].button("Clear", use_container_width=True)

    if clear_clicked:
        st.session_state.last_result = None
        st.session_state.last_topic = ""
        st.session_state.run_duration = None
        st.rerun()

    ready, missing = has_required_keys()
    if run_clicked:
        if not topic.strip():
            st.warning("Enter a research topic first.")
        elif not ready:
            st.error(f"Add these keys to your .env file first: {', '.join(missing)}")
        else:
            with st.spinner("Running the full agent pipeline..."):
                try:
                    run_pipeline(topic.strip())
                except Exception as exc:
                    st.exception(exc)

    if st.session_state.last_result:
        render_result(st.session_state.last_result)
    else:
        st.markdown(
            """
            <div class="status-box">
                <strong>Ready when you are.</strong>
                <div class="small-muted">Enter a topic and run the pipeline to generate a report with feedback.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
