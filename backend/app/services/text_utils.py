import httpx
import re
from bs4 import BeautifulSoup


async def extract_article_text(url: str) -> str:
    """
    Fetch and extract readable text from a news article URL.
    Uses simple paragraph-based extraction for clarity.
    """

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)

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
