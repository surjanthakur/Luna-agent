import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


@tool()
def get_weather(city: str):
    """return the current weather info for a given city"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"Weather of {city} is {response.text}"


@tool()
def web_search(query: str):
    """return the information from internet based on  query asked by user"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": os.getenv("GOOGLE_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
    }

    try:
        response = requests.get(url, params=params)
        results = response.json()

        informations = []
        if "items" in results:
            for item in results["items"]:
                informations.append(
                    f"{item['title']}: {item['link']}\n{item.get('snippet', '')}"
                )

        return "\n\n".join(informations[:5])  # Top 5 results
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool()
def get_location_by_ip(ip: str):
    """
    Get approx location from IP address.
    If no IP is given, auto-detects using 'ipinfo.io'.
    """
    try:
        url = f"https://ipinfo.io/{ip}/json" if ip else "https://ipinfo.io/json"
        res = requests.get(url)
        data = res.json()
        return {
            "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc"),  # latitude,longitude
        }
    except Exception as e:
        return {"error": str(e)}
