from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, num_results: int = 3) -> list[dict]:
    """Return Tavily search results with title, URL, and snippet fields."""
    results = tavily.search(query=query, num_results=num_results)
    return results.get("results", [])


def format_search_results(results: list[dict]) -> str:
    out = []
    for result in results:
        out.append(
            "Title: {title}\nURL: {url}\nSnippet: {snippet}\n".format(
                title=result.get("title", "Untitled"),
                url=result.get("url", ""),
                snippet=result.get("content", "")[:500],
            )
        )
    return "\n".join(out)


def scrape_page(url: str) -> str:
    """Scrape the content of a given URL and return readable page text."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/58.0.3029.110 Safari/537.3"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:5000]
    except requests.exceptions.RequestException as e:
        return f"An error occurred while trying to scrape the URL: {e}"


@tool
def web_search(query: str)-> str:
    """"Search the web for recent and reliable impormation on any topic. returns title, returns URL and snippets"""
    return format_search_results(search_web(query=query, num_results=3))

@tool
def scrape_url(url: str) -> str:
    """Scrape the content of a given URL and return the text."""
    return scrape_page(url)
