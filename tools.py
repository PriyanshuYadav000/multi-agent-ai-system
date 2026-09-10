import os
import re

import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient


load_dotenv()


# ============================================================
# SECRET MANAGEMENT
# ============================================================

def get_secret(name: str):
    """
    Get a secret from Streamlit Secrets first,
    then fall back to environment variables.
    """
    try:
        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return os.getenv(name)


TAVILY_API_KEY = get_secret("TAVILY_API_KEY")
OPENWEATHER_API_KEY = get_secret("OPENWEATHER_API_KEY")


# ============================================================
# TAVILY CLIENT
# ============================================================

if not TAVILY_API_KEY:
    raise RuntimeError(
        "TAVILY_API_KEY is not configured."
    )


tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ============================================================
# WEATHER DETECTION
# ============================================================

def is_weather_query(query: str) -> bool:
    """
    Detect weather-related queries in English and Hindi.
    """

    if not query:
        return False

    text = query.lower().strip()

    weather_keywords = [
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

    return any(
        keyword in text
        for keyword in weather_keywords
    )


# ============================================================
# WEATHER LOCATION EXTRACTION
# ============================================================

def extract_weather_location(query: str) -> str:
    """
    Extract city/location from weather-related queries.
    """

    if not query:
        return ""

    text = query.strip()

    patterns = [
        # English
        r"\bweather\s+(?:in|of|for|at)\s+(.+)",
        r"\btemperature\s+(?:in|of|for|at)\s+(.+)",
        r"\bforecast\s+(?:in|of|for|at)\s+(.+)",
        r"\bclimate\s+(?:in|of|for|at)\s+(.+)",
        r"\bhumidity\s+(?:in|of|for|at)\s+(.+)",
        r"\brain(?:ing)?\s+(?:in|at)\s+(.+)",
        r"\bsnow(?:ing)?\s+(?:in|at)\s+(.+)",
        r"\bwind\s+(?:in|at)\s+(.+)",

        r"\b(.+?)\s+weather\b",
        r"\b(.+?)\s+temperature\b",
        r"\b(.+?)\s+forecast\b",

        # Hindi
        r"(.+?)\s+का\s+मौसम",
        r"(.+?)\s+का\s+तापमान",
        r"मौसम\s+(?:में|का|के|की|पर)\s+(.+)",
        r"तापमान\s+(?:में|का|के|की|पर)\s+(.+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:

            location = match.group(1).strip()

            location = re.sub(
                r"[?.!,]+$",
                "",
                location,
            ).strip()

            if location:
                return location

    # Fallback cleanup.
    cleaned = text

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

    for word in weather_words:

        cleaned = re.sub(
            rf"\b{re.escape(word)}\b",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = cleaned.replace(
            word,
            "",
        )

    filler_words = [
        "in",
        "of",
        "for",
        "at",
        "is",
        "the",
        "what",
        "how",
        "today",
        "tomorrow",
    ]

    for word in filler_words:

        cleaned = re.sub(
            rf"\b{re.escape(word)}\b",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    ).strip()

    cleaned = re.sub(
        r"[?.!,]+$",
        "",
        cleaned,
    ).strip()

    return cleaned


# ============================================================
# WEB SEARCH
# ============================================================

@tool
def web_search(query: str) -> str:
    """
    Search the live web using Tavily.
    """

    try:

        if not query:
            return "Search query is empty."

        query = query.strip()

        results = tavily.search(
            query=query,
            max_results=5,
            search_depth="advanced",
        )

        output = []

        for index, result in enumerate(
            results.get("results", []),
            start=1,
        ):

            title = result.get(
                "title",
                "",
            )

            url = result.get(
                "url",
                "",
            )

            content = result.get(
                "content",
                "",
            )

            output.append(
                f"Source {index}\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Snippet: {content[:900]}"
            )

        if not output:

            return (
                "No relevant web search results found."
            )

        return "\n\n---\n\n".join(
            output
        )

    except Exception as exc:

        return (
            f"Web search failed: {exc}"
        )


# ============================================================
# URL SCRAPER
# ============================================================

@tool
def scrape_url(url: str) -> str:
    """
    Scrape readable content from a webpage.
    """

    try:

        if not url:
            return "URL is empty."

        response = requests.get(
            url,
            timeout=12,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/139.0 Safari/537.36"
                ),
            },
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "noscript",
                "form",
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        return text[:8000]

    except requests.exceptions.Timeout:

        return (
            "Could not scrape URL: request timed out."
        )

    except requests.exceptions.HTTPError as exc:

        return (
            f"Could not scrape URL: HTTP error: {exc}"
        )

    except requests.exceptions.RequestException as exc:

        return (
            f"Could not scrape URL: network error: {exc}"
        )

    except Exception as exc:

        return (
            f"Could not scrape URL: {exc}"
        )


# ============================================================
# LIVE WEATHER
# ============================================================

@tool
def get_live_weather(city: str) -> str:
    """
    Get current weather using OpenWeather.
    """

    if not city:
        return "Weather location is empty."

    if not OPENWEATHER_API_KEY:
        return (
            "OPENWEATHER_API_KEY is not configured."
        )

    try:

        # ----------------------------------------------------
        # GEOCODING
        # ----------------------------------------------------

        geo_response = requests.get(
            "https://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": city,
                "limit": 1,
                "appid": OPENWEATHER_API_KEY,
            },
            timeout=10,
        )

        geo_response.raise_for_status()

        locations = geo_response.json()

        if not locations:

            return (
                f"Could not find city: {city}"
            )

        location = locations[0]

        latitude = location.get(
            "lat"
        )

        longitude = location.get(
            "lon"
        )

        if latitude is None or longitude is None:

            return (
                f"Could not determine coordinates for: {city}"
            )

        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        weather_response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=10,
        )

        weather_response.raise_for_status()

        data = weather_response.json()

        weather_list = data.get(
            "weather",
            [],
        )

        if not weather_list:

            return (
                f"No weather information available for {city}."
            )

        weather = weather_list[0]

        main = data.get(
            "main",
            {},
        )

        wind = data.get(
            "wind",
            {},
        )

        return (
            f"City: {data.get('name', city)}\n"
            f"Country: {location.get('country', '')}\n"
            f"Temperature: {main.get('temp', 'N/A')}°C\n"
            f"Feels Like: {main.get('feels_like', 'N/A')}°C\n"
            f"Humidity: {main.get('humidity', 'N/A')}%\n"
            f"Condition: {weather.get('description', 'N/A')}\n"
            f"Wind Speed: {wind.get('speed', 0)} m/s\n"
            f"Pressure: {main.get('pressure', 'N/A')} hPa"
        )

    except requests.exceptions.Timeout:

        return (
            "Weather lookup failed: request timed out."
        )

    except requests.exceptions.HTTPError as exc:

        return (
            f"Weather API request failed: {exc}"
        )

    except requests.exceptions.RequestException as exc:

        return (
            f"Weather network error: {exc}"
        )

    except Exception as exc:

        return (
            f"Weather lookup failed: {exc}"
        )


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

live_weather = get_live_weather