import requests
import re

JIKAN_BASE_URL = "https://api.jikan.moe/v4"



def validate_search_query(query):
    query = query.strip()

    if not query:
        return False, "Please enter an anime title.", ""

    if len(query) < 3:
        return False, "Search must be at least 3 characters long.", ""

    if len(query) > 80:
        return False, "Search must be 80 characters or less.", ""

    if not re.match(r"^[a-zA-Z0-9\s:.'!?&\-/;]+$", query):
        return False, "Search contains invalid characters.", ""

    return True, "", query


def search_anime(query, limit=10):

    is_valid, message, query = validate_search_query(query)

    if not is_valid:
        return False, message, []
    

    url = f"{JIKAN_BASE_URL}/anime"

    #params for jikan to take 
    params = {
        "q": query,
        "sfw": "true",
        "limit": limit
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 429:
            return False, "Too many requests. Please wait a moment and try again.", []

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException:
        return False, "Could not connect to the anime search API.", []

    results = []

    #loop thru 
    for anime in data.get("data", []):

    #loop thru to get genres
        genres = anime.get("genres", [])
        genre_names = []

        for genre in genres:
            genre_names.append(genre.get("name"))


        #create genre text to be displayed/saved
        genre_text = ", ".join(genre_names) if genre_names else "Unknown"

        image_url = (
            anime.get("images", {})
            .get("jpg", {})
            .get("large_image_url")
        )

        #extract essential data from anime objs in data list
        anime_data = {
            "mal_id": anime.get("mal_id"),
            "title": anime.get("title"),
            "image_url": image_url,
            "episodes": anime.get("episodes"),
            "genre": genre_text,
            "synopsis": anime.get("synopsis"),
            "score": anime.get("score"),
            "status": anime.get("status"),
            "type": anime.get("type"),
            "year": anime.get("year")
        }

        results.append(anime_data)

    return True, "", results