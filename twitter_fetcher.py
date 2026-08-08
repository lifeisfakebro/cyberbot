"""
سحب تغريدات من حسابات X عن طريق RSS الخاص بـ Nitter (طريقة غير رسمية).

تنبيه مهم:
X ألغت أي وصول مجاني رسمي للقراءة اعتباراً من فبراير 2026.
الطريقة هذي تعتمد على nitter instances عامة، وهذي الـ instances
غير مستقرة وممكن تتوقف أو تتغير بأي وقت بدون إشعار.
البرنامج مصمم يتجاوز أي فشل هنا ويكمل شغله الطبيعي على مصادر RSS.

لو حصلت على وصول رسمي لـ X API مستقبلاً، أفضل حل هو استبدال
هذا الملف بالكامل باستدعاء رسمي لـ X API v2 (endpoint: /2/users/:id/tweets)
بدل الاعتماد على nitter.
"""
import feedparser
import requests

USER_AGENT = "Mozilla/5.0 (compatible; CyberNewsBot/1.0)"


def _try_instance(instance_url: str, username: str, timeout: int) -> list:
    """يحاول يجيب RSS feed حساب معين من instance واحد."""
    feed_url = f"{instance_url.rstrip('/')}/{username}/rss"
    items = []
    try:
        resp = requests.get(feed_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        if resp.status_code != 200:
            return items

        parsed = feedparser.parse(resp.content)
        if not parsed.entries:
            return items

        for entry in parsed.entries:
            items.append({
                "title": entry.get("title", "")[:200],
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "source": f"X @{username}",
                "published_ts": 0,
                "origin": "twitter",
            })
    except Exception:
        pass

    return items


def fetch_account_tweets(username: str, nitter_instances: list, timeout: int = 15) -> list:
    """يجرب كل الـ instances بالترتيب لحد ما يوحد نجاح، أو يرجع فاضي لو كلها فشلت."""
    for instance in nitter_instances:
        items = _try_instance(instance, username, timeout)
        if items:
            print(f"  ✓ تم سحب @{username} من {instance}")
            return items
    print(f"  [تحذير] تعذر سحب @{username} من كل الـ instances المتاحة")
    return []


def fetch_all_twitter(twitter_accounts: list, nitter_instances: list, timeout: int = 15) -> list:
    """يسحب تغريدات كل الحسابات المحددة في الإعدادات."""
    all_items = []
    if not twitter_accounts:
        return all_items
    if not nitter_instances:
        print("  [تحذير] لا يوجد nitter instances في الإعدادات، تم تجاوز جزء X")
        return all_items

    for username in twitter_accounts:
        print(f"جاري سحب حساب X: @{username}")
        all_items.extend(fetch_account_tweets(username, nitter_instances, timeout))

    return all_items
