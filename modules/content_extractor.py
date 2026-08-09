"""
استخراج نص المقال الكامل (وليس مجرد الملخص) من صفحة الخبر،
بالإضافة إلى الصورة الرئيسية.
"""
import re
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; CyberNewsBot/1.0)"

CONTENT_SELECTORS = [
    "article",
    {"itemprop": "articleBody"},
    {"class": "entry-content"},
    {"class": "post-content"},
    {"class": "article-content"},
    {"class": "article-body"},
    {"class": "content-body"},
    "main",
]


def _clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_article_content(article_url: str, timeout: int = 15) -> dict:
    result = {"image": None, "text": None}
    if not article_url:
        return result

    try:
        resp = requests.get(
            article_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
        )
        if resp.status_code != 200:
            return result

        soup = BeautifulSoup(resp.content, "html.parser")

        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            result["image"] = og_image["content"]
        else:
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image and twitter_image.get("content"):
                result["image"] = twitter_image["content"]

        container = None
        for selector in CONTENT_SELECTORS:
            if isinstance(selector, str):
                container = soup.find(selector)
            else:
                container = soup.find(attrs=selector)
            if container:
                break

        if container is None:
            container = soup.body

        if container:
            paragraphs = container.find_all("p")
            text_parts = [
                p.get_text(strip=True)
                for p in paragraphs
                if len(p.get_text(strip=True)) > 40
            ]
            full_text = "\n\n".join(text_parts)
            result["text"] = _clean_text(full_text) if full_text else None

        return result
    except Exception:
        return result
