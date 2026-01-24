import httpx
import re
from bs4 import BeautifulSoup


async def extract_article_text(url: str) -> str:
    """
    Fetch and extract readable text from a news article URL.
    Uses simple paragraph-based extraction for clarity.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch article content")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    paragraphs = soup.find_all("p")

    text = " ".join(p.get_text() for p in paragraphs)

    # Clean excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
