from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app = FastAPI(title="Universal Article Scraper API")

API_KEY = None  # Optional API key


class ArticleResponse(BaseModel):
    url: str
    title: str | None
    author: str | None
    published_date: str | None
    body: str


def scrape_with_playwright(url: str) -> ArticleResponse:
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000, wait_until="networkidle")

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")

        # TITLE
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        # AUTHOR
        author = None
        for selector in ["[class*=author]", "[class*=Author]", "[class*=byline]", "[class*=ByLine]"]:
            tag = soup.select_one(selector)
            if tag:
                author = tag.get_text(strip=True)
                break

        # DATE
        date = None
        time_tag = soup.find("time")
        if time_tag:
            date = time_tag.get_text(strip=True)

        # BODY
        paragraphs = soup.find_all("p")
        body = "\n".join([p.get_text(strip=True) for p in paragraphs])

        return ArticleResponse(url=url, title=title, author=author, published_date=date, body=body)

    except Exception as e:
        raise HTTPException(500, f"Scraping failed: {str(e)}")


@app.get("/parse", response_model=ArticleResponse)
def parse(url: str, key: str | None = None):
    if API_KEY and key != API_KEY:
        raise HTTPException(401, "Invalid API key")
    return scrape_with_playwright(url)
