"""
استخراج صورة رئيسية من صفحة الخبر عن طريق وسوم og:image / twitter:image.
"""
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; CyberNewsBot/1.0)"


def extract_image_url(article_url: str, timeout: int = 15) -> str | None:
    """يرجع رابط الصورة الرئيسية للخبر، أو None لو ما لقى شي."""
    if not article_url:
        return None

    try:
        resp = requests.get(
            article_url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.content, "html.parser")

        # الأولوية لوسم og:image لأنه أشيع وأدق وسم للصورة الرئيسية
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]

        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]

        return None
    except Exception:
        return None
