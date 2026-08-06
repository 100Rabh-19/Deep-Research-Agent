# Multi-Agent Research Studio

A Streamlit app that runs a small LangChain-based research pipeline. It searches the web with Tavily, scrapes selected sources, writes a structured research report with a Hugging Face-hosted model, and reviews the report with a critic chain.

## Features

- Streamlit interface for entering a research topic
- Tavily-powered web search
- Web page scraping with BeautifulSoup
- LangChain writer and critic chains
- Report, feedback, source, and scraped-content tabs
- Markdown report download

## Project Structure

```text
.
├── Agent.py              # LLM setup plus writer and critic chains
├── Pipeline.py           # End-to-end research workflow
├── main.py               # Streamlit app
├── tools.py              # Search and scraping tools
├── requirements.txt      # Python dependencies
└── .env.example          # Required environment variable template
```

## Requirements

- Python 3.10 or newer
- Hugging Face API token
- Tavily API key

## Setup

1. Clone the repository:

```bash
git clone <your-repository-url>
cd Multi_Agent
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your local environment file:

```bash
cp .env.example .env
```

Then update `.env` with your real keys:

```text
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## Run the App

```bash
streamlit run main.py
```

Open the local Streamlit URL shown in the terminal, enter a research topic, and run the pipeline.

## Run from the CLI

You can also run the pipeline directly:

```bash
python Pipeline.py
```

## Notes

- Do not commit your `.env` file or API keys.
- Search quality depends on the Tavily results for the topic.
- Scraping may fail for pages that block automated requests or require JavaScript.

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for the basic workflow.
