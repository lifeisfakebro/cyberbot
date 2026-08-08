"""
سحب الأخبار من مواقع RSS.
كل خبر يرجع كـ dict فيه: title, link, summary, source, published
"""
import feedparser
import time


def fetch_from_rss(feed_url: str, timeout: int = 15) -> list:
    """يقرأ خبر RSS ويرجع قائمة أخبار. لو فشل المصدر، يرجع قائمة فاضية بدون ما يوقف البرنامج."""
    items = []
    try:
        parsed = feedparser.parse(feed_url)

        if parsed.bozo and not parsed.entries:
            print(f"  [تحذير] تعذر قراءة المصدر: {feed_url}")
            return items

        source_name = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            title = entry.get("title", "بدون عنوان")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))

            published = entry.get("published_parsed") or entry.get("updated_parsed")
            published_ts = time.mktime(published) if published else 0

            if link:
                items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": source_name,
                    "published_ts": published_ts,
                    "origin": "rss",
                })
    except Exception as e:
        print(f"  [خطأ] فشل سحب المصدر {feed_url}: {e}")

    return items


def fetch_all_rss(rss_sources: list, timeout: int = 15) -> list:
    """يسحب من كل مصادر RSS المحددة في الإعدادات."""
    all_items = []
    for url in rss_sources:
        print(f"جاري سحب: {url}")
        all_items.extend(fetch_from_rss(url, timeout))
    return all_items
