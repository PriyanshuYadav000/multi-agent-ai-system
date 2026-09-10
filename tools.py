import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
import streamlit as st

load_dotenv()

TAVILY_API_KEY = st.secrets.get(
    "TAVILY_API_KEY",
    os.getenv("TAVILY_API_KEY")
)

OPENWEATHER_API_KEY = st.secrets.get(
    "OPENWEATHER_API_KEY",
    os.getenv("OPENWEATHER_API_KEY")
)

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY is not configured.")

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic."""
    try:
        results = tavily.search(
            query=query,
            max_results=5
        )

        output = []

        for result in results.get("results", []):
            output.append(
                f"Title: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Snippet: {result.get('content', '')[:500]}\n"
            )

        return "\n----\n".join(output)

    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        return soup.get_text(
            separator=" ",
            strip=True
        )[:5000]

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


@tool
def live_weather(city: str) -> str:
    """Get current live weather for a city."""

    try:
        if not OPENWEATHER_API_KEY:
            return "OPENWEATHER_API_KEY is not configured."

        geo_response = requests.get(
            "https://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": city,
                "limit": 1,
                "appid": OPENWEATHER_API_KEY
            },
            timeout=10
        )

        geo_response.raise_for_status()

        locations = geo_response.json()

        if not locations:
            return f"Could not find location: {city}"

        lat = locations[0]["lat"]
        lon = locations[0]["lon"]

        weather_response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            },
            timeout=10
        )

        weather_response.raise_for_status()

        data = weather_response.json()

        return (
            f"City: {data['name']}\n"
            f"Country: {data['sys']['country']}\n"
            f"Temperature: {data['main']['temp']} °C\n"
            f"Feels Like: {data['main']['feels_like']} °C\n"
            f"Humidity: {data['main']['humidity']}%\n"
            f"Weather: {data['weather'][0]['description']}\n"
            f"Wind Speed: {data['wind']['speed']} m/s\n"
            f"Pressure: {data['main']['pressure']} hPa"
        )

    except Exception as e:
        return f"Weather lookup failed: {str(e)}"