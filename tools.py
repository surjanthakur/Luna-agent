import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
import os, requests, webbrowser
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.utilities import WikipediaAPIWrapper

load_dotenv()


@tool()
def get_weather(city: str):
    """return the current weather info for a given city"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"Weather of {city} is {response.text}"


@tool
def web_search(query: str) -> str:
    """Return the new relevant information from internet based on query asked by user"""

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": os.getenv("GOOGLE_API_KEY"),  #  Google API key
        "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),  # CSE ID
    }

    try:
        response = requests.get(url, params=params)
        results = response.json()

        informations = []
        if "items" in results:
            for item in results["items"]:
                informations.append(
                    f"{item['title']} - {item['link']}\n{item.get('snippet', '')}"
                )

        return "\n\n".join(informations[:5]) if informations else "No results found."
    except Exception as e:
        return f"Error performing web search: {str(e)}"


# this tool runs only locally on your machine
def play_song(song_name: str):
    """Search YouTube for a song and return the video link to play song"""
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": song_name,
        "type": "video",
        "maxResults": 1,
        "key": os.getenv("GOOGLE_API_KEY"),
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        return "No song found."

    video_id = data["items"][0]["id"]["videoId"]
    song_url = f"https://www.youtube.com/watch?v={video_id}"
    return webbrowser.open_new_tab(song_url)


@tool()
def wikipidia_search(query: str):
    "use this tool when user ask query about history , facts , research papers , new research papers or news related: tech or political or biography about person"

    wiki_client = WikipediaAPIWrapper(lang="en", wiki_client=any)

    retriever = WikipediaRetriever(wiki_client=wiki_client, top_k_results=3)

    docs = retriever.invoke(query)

    return "\n\n".join([f"content: {doc.page_content}" for doc in docs])
