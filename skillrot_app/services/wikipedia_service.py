import requests
from typing import Optional
from urllib.parse import quote

WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

HEADERS = {
    "User-Agent": "SkillRotApp/1.0 (skillrot@example.com)"
}

# 🔹 Common short forms expansion
SHORT_FORM_MAP = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "dsa": "data structures and algorithms",
    "dbms": "database management system",
    "os": "operating system",
    "oop": "object oriented programming",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "dl": "deep learning"
}

# 🔹 Irrelevant topic filters
IRRELEVANT_KEYWORDS = [
    "species", "snake", "animal", "bird",
    "film", "village", "district",
    "album", "band", "song",
    "river", "mountain"
]


def expand_short_forms(text: str) -> str:
    words = text.lower().split()
    expanded = []
    for w in words:
        expanded.append(SHORT_FORM_MAP.get(w, w))
    return " ".join(expanded)


def is_relevant_page(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()
    for word in IRRELEVANT_KEYWORDS:
        if word in text:
            return False
    return True


def fetch_wikipedia_article(topic: str) -> Optional[dict]:
    """
    Fetch Wikipedia article for refined subtopic.
    """

    try:
        topic = expand_short_forms(topic)

        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "format": "json"
        }

        search_response = requests.get(
            WIKI_SEARCH_URL,
            params=search_params,
            headers=HEADERS,
            timeout=5
        )

        if search_response.status_code != 200:
            return None

        search_data = search_response.json()
        search_results = search_data.get("query", {}).get("search", [])

        if not search_results:
            return None

        # 🔥 Try top 3 results
        for result in search_results[:3]:
            page_title = result["title"]
            encoded_title = quote(page_title)

            summary_response = requests.get(
                f"{WIKI_SUMMARY_URL}{encoded_title}",
                headers=HEADERS,
                timeout=5
            )

            if summary_response.status_code != 200:
                continue

            summary_data = summary_response.json()

            title = summary_data.get("title")
            summary = summary_data.get("extract")
            url = summary_data.get("content_urls", {}) \
                               .get("desktop", {}) \
                               .get("page")

            if not title or not summary:
                continue

            if not is_relevant_page(title, summary):
                continue

            return {
                "title": title,
                "summary": summary,
                "url": url,
                "type": "article"
            }

        return None

    except Exception:
        return None