from Agent import critic_chain, write_report
from tools import format_search_results, scrape_page, search_web

def _safe_print(*values) -> None:
    text = " ".join(str(value) for value in values)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))

def run_research_pipeline(topic: str)->  dict:

    state = {}

    

    search_results = search_web(
        query=f"recent reliable information about {topic}",
        num_results=5,
    )
    state["search_items"] = search_results
    state["urls"] = [result.get("url", "") for result in search_results if result.get("url")]
    state["search_results"] = format_search_results(search_results)
    _safe_print(state["search_results"])

        #step 2 - reader agent 
    _safe_print("\n"+" ="*50)
    _safe_print("step 2 - Scraping top resources ...")
    _safe_print("="*50)

    scraped_pages = []
    for index, url in enumerate(state["urls"][:3], start=1):
        content = scrape_page(url)
        scraped_pages.append(
            {
                "url": url,
                "content": content,
            }
        )
        _safe_print(f"Scraped source {index}: {url}")

    state["scraped_pages"] = scraped_pages
    state["scraped_content"] = "\n\n".join(
        f"SOURCE {index}: {page['url']}\n{page['content']}"
        for index, page in enumerate(scraped_pages, start=1)
    )
    _safe_print("\nscraped content\n", state["scraped_content"])


    # step 3 - writer agent
    _safe_print("\n"+" ="*50)
    _safe_print("step 3 - Writer agent is creating the report ...")
    _safe_print("="*50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETEILED SCRAPED CONTENT:\n{state['scraped_content']}"

    )

    state["report"] = write_report(topic=topic, research=research_combined)

    _safe_print("\nreport\n", state["report"])


    # critic report

    _safe_print("\n"+" ="*50)
    _safe_print("step 4 - Critic agent is evaluating the report ...")
    _safe_print("="*50)
    state["feedback"] = critic_chain.invoke(
        {
            "report": state["report"]
        }
    )
    _safe_print("\ncritic_feedback\n", state["feedback"])


    return state

if __name__ == "__main__":
    topic = input("\n Enter your Topic\n")
    run_research_pipeline(topic)
