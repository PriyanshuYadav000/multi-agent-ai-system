import os
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


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
# WEB SEARCH
# ============================================================

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information.
    Returns titles, URLs and snippets.
    """

    results = tavily.search(
        query=query,
        max_results=5,
    )

    output = []

    for result in results.get("results", []):

        output.append(
            f"Title: {result.get('title', 'Unknown')}\n"
            f"URL: {result.get('url', '')}\n"
            f"Snippet: "
            f"{result.get('content', '')[:500]}\n"
        )

    return "\n----\n".join(output)


# ============================================================
# WEB SCRAPER
# ============================================================

@tool
def scrape_url(url: str) -> str:
    """
    Scrape clean webpage text from a URL.
    """

    try:

        response = requests.get(
            url,
            timeout=8,
            headers={
                "User-Agent": "Mozilla/5.0"
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
                "noscript",
            ]
        ):
            tag.decompose()

        return soup.get_text(
            separator=" ",
            strip=True,
        )[:5000]

    except Exception as exc:

        return (
            f"Could not scrape URL: {str(exc)}"
        )


# ============================================================
# WEATHER QUERY DETECTION
# ============================================================

def is_weather_query(
    query: str,
) -> bool:

    text = query.lower()

    keywords = [
        "weather",
        "temperature",
        "forecast",
        "rain",
        "raining",
        "humidity",
        "wind",
        "climate",

        # Hindi
        "मौसम",
        "तापमान",
        "पूर्वानुमान",
        "बारिश",
        "वर्षा",
        "हवा",
        "आर्द्रता",

        # Hinglish
        "mausam",
        "barish",
        "taapman",
        "temperature",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# ============================================================
# WEATHER LOCATION EXTRACTION
# ============================================================

def extract_weather_location(
    query: str,
) -> str:

    original = query.strip()
    text = original.lower()

    phrases = [
        "what is the weather in",
        "what's the weather in",
        "weather in",
        "weather at",
        "weather for",
        "temperature in",
        "temperature at",
        "forecast in",
        "forecast for",
        "today's weather in",
        "today weather in",

        # Hindi
        "मौसम in",
        "मौसम में",
        "मौसम कैसा है",
        "का मौसम",
        "के मौसम",
        "तापमान",
        
        # Hinglish
        "mausam in",
        "mausam kaisa hai",
        "mausam batao",
        "temperature in",
        "barish in",
    ]

    for phrase in phrases:

        index = text.find(
            phrase.lower()
        )

        if index != -1:

            location = original[
                index + len(phrase):
            ]

            location = location.strip(
                " ?.,:।"
            )

            location = location.replace(
                "today",
                "",
            ).strip()

            location = location.replace(
                "aaj",
                "",
            ).strip()

            return location

    return original


# ============================================================
# OPENWEATHER
# ============================================================

def get_live_weather(
    location: str,
) -> str:

    if not OPENWEATHER_API_KEY:

        return (
            "OpenWeather API key is not configured. "
            "Please add OPENWEATHER_API_KEY."
        )

    location = location.strip()

    if not location:

        return (
            "Please mention a city or location."
        )

    try:

        geocode_url = (
            "https://api.openweathermap.org/"
            "geo/1.0/direct"
        )

        geo_response = requests.get(
            geocode_url,
            params={
                "q": location,
                "limit": 1,
                "appid": OPENWEATHER_API_KEY,
            },
            timeout=10,
        )

        geo_response.raise_for_status()

        locations = geo_response.json()

        if not locations:

            return (
                f"Could not find weather location: "
                f"{location}"
            )

        latitude = locations[0]["lat"]
        longitude = locations[0]["lon"]

        weather_url = (
            "https://api.openweathermap.org/"
            "data/2.5/weather"
        )

        weather_response = requests.get(
            weather_url,
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

        weather = data["weather"][0]

        return (
            f"Location: "
            f"{data['name']}, "
            f"{data['sys']['country']}\n"
            f"Temperature: "
            f"{data['main']['temp']}°C\n"
            f"Feels Like: "
            f"{data['main']['feels_like']}°C\n"
            f"Condition: "
            f"{weather['description']}\n"
            f"Humidity: "
            f"{data['main']['humidity']}%\n"
            f"Wind Speed: "
            f"{data['wind']['speed']} m/s\n"
            f"Pressure: "
            f"{data['main']['pressure']} hPa"
        )

    except Exception as exc:

        return (
            f"Weather lookup failed: {str(exc)}"
        )


# ============================================================
# WEATHER TOOL
# ============================================================

@tool
def live_weather(
    location: str,
) -> str:
    """
    Get current live weather for a location
    using OpenWeather.
    """

    return get_live_weather(
        location
    )