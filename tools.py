from langchain.tools import tool
import requests  # for web scraping
from bs4 import BeautifulSoup  # for web scraping
from tavily import TavilyClient  # for Tavily API
import os  # for environment variables
from dotenv import load_dotenv  # for loading environment variables
from rich import print

load_dotenv()


tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a topic using the Tavily API.

    Return Title, URL and snippet of the top 5 results.
    If no results are found, return a message indicating that no results were found.
    """

    try:
        response = tavily_client.search(
            query=query,
            max_results=5
        )
        results = response.get("results", [])

        if not results:
            return "No search results were found."

        out = []

        for r in results:
            out.append(
                f"Title: {r.get('title', 'No title')}\n"
                f"URL: {r.get('url', 'No URL')}\n"
                f"Snippet: {r.get('content', 'No snippet available')}\n"
            )

        return "\n-----------\n".join(out)

    except Exception as e:

        return f"An error occurred while performing the web search: {e}"

@tool
def web_scrape(url: str) -> str:
    """
    Scrape the content of a web page given its URL.

    Return the text content of the page.
    If the page cannot be scraped, return a message indicating that the page could not be scraped.
    """

    try:

        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style","nav","footer","header"]):
            tag.decompose()  # Remove script and style tags

        if response.status_code != 200:
            return f"Failed to retrieve the page. Status code: {response.status_code}"
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract text from the page
        text_content = soup.get_text(separator="\n", strip=True)[:3000]  # Limit to first 30,000 characters
        return text_content

    except Exception as e:
        return f"An error occurred while scraping the web page: {e}"

print(
    web_search.invoke(
        "https://www.cricinfo.com/"
    )
)