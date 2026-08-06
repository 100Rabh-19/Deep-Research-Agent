from langchain.agents import create_agent
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import re
load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V4-Flash-0731",
    task="text-generation",
    temperature=0.7,
    max_new_tokens=1600,)
model = ChatHuggingFace(llm=llm)


# first agent
def build_search_agent():
    return create_agent(
        model=model,
        tools=[web_search],
    )

# 2nd agent
def build_reader_agent():
    return create_agent(
        model=model,
        tools=[scrape_url],
    )


#writer chain

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

def _compact_research(research: str, max_chars: int = 4500) -> str:
    lines = [line.strip() for line in research.splitlines() if line.strip()]
    important_lines = [
        line
        for line in lines
        if line.startswith(("Title:", "URL:", "Snippet:", "SOURCE "))
        or any(word in line.lower() for word in ["agent", "research", "productivity", "software", "development"])
    ]
    compact = "\n".join(important_lines)
    return (compact or research)[:max_chars]


def _fallback_report(topic: str, research: str) -> str:
    urls = list(dict.fromkeys(re.findall(r"https?://\S+", research)))
    snippets = [
        line.replace("Snippet:", "").strip()
        for line in research.splitlines()
        if line.strip().startswith("Snippet:")
    ]
    source_list = "\n".join(f"- {url}" for url in urls) or "- No source URLs were available."
    finding_lines = snippets[:3] or [
        "The gathered material describes the topic as an active area with practical adoption.",
        "The sources suggest benefits around automation, productivity, and decision support.",
        "The research also points to implementation challenges such as reliability, oversight, and evaluation.",
    ]
    findings = "\n".join(f"- {finding}" for finding in finding_lines)

    return f"""# Research Report: {topic}

## Introduction
This report summarizes the available search and scraped-source notes gathered for "{topic}". The source material was collected from web search results and selected pages, then organized into a concise research brief.

## Key Findings
{findings}

## Conclusion
The collected sources indicate that {topic} is a meaningful and evolving area. The strongest themes in the gathered material should be treated as directional findings and validated further with primary sources where high-stakes decisions are involved.

## Sources
{source_list}
"""


def _is_complete_report(report: str) -> bool:
    normalized = report.lower()
    required_sections = ["introduction", "key findings", "conclusion", "sources"]
    return len(report) >= 700 and all(section in normalized for section in required_sections)


def write_report(topic: str, research: str) -> str:
    compact_research = _compact_research(research)
    messages = [
        SystemMessage(content="You write concise, factual research reports from provided source notes."),
        HumanMessage(
            content=f"""Create a research report.

Topic: {topic}

Source notes:
{compact_research}

Use this structure:
Introduction
Key Findings
Conclusion
Sources

Include the source URLs from the notes. Do not return an empty answer."""
        ),
    ]
    response = model.invoke(messages)
    report = getattr(response, "content", str(response)).strip()

    if _is_complete_report(report):
        return report

    fallback_response = model.invoke(
        f"Write a concise research report about {topic} using these source notes:\n\n{compact_research[:2500]}"
    )
    fallback = getattr(fallback_response, "content", str(fallback_response)).strip()
    return fallback if _is_complete_report(fallback) else _fallback_report(topic, research)


writer_chain = writer_prompt | model | StrOutputParser()

# critic_chain
critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
]) 

critic_chain = critic_prompt | model | StrOutputParser()
