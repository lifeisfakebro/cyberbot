"""
بوت الأخبار السيبرانية - الملف الرئيسي

يسحب أخبار من مصادر RSS وحسابات X، يستخرج صورة ونص كامل لكل خبر،
ويرسلها على قناة/شات تيليجرام. يحفظ سجل الأخبار المرسلة
عشان ما يكرر إرسال نفس الخبر.
"""
import os
import sys
import json
import time

from modules.rss_fetcher import fetch_all_rss
from modules.twitter_fetcher import fetch_all_twitter
from modules.content_extractor import extract_article_content
from modules.telegram_sender import send_news_item
from modules.state_manager import load_state, save_state, is_new, mark_seen

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[خطأ فادح] لازم تحدد TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID كمتغيرات بيئة.")
        sys.exit(1)

    config = load_config()
    timeout = config.get("request_timeout_seconds", 15)
    max_per_run = config.get("max_items_per_run", 10)

    print("=== بدء سحب الأخبار ===")
    rss_items = fetch_all_rss(config.get("rss_sources", []), timeout)
    twitter_items = fetch_all_twitter(
        config.get("twitter_accounts", []),
        config.get("nitter_instances", []),
        timeout,
    )

    all_items = rss_items + twitter_items
    print(f"إجمالي الأخبار المسحوبة: {len(all_items)}")

    all_items.sort(key=lambda x: x.get("published_ts", 0), reverse=True)

    seen_hashes = load_state()
    new_items = []
    for item in all_items:
        if item.get("link") and is_new(item["link"], seen_hashes):
            new_items.append(item)

    print(f"أخبار جديدة لم تُرسل من قبل: {len(new_items)}")

    if not new_items:
        print("لا يوجد أخبار جديدة بهذه الجولة.")
        return

    items_to_send = new_items[:max_per_run]

    sent_count = 0
    for item in items_to_send:
        print(f"جاري إرسال: {item['title'][:60]}")

        image_url = None
        full_text = None
        if item.get("origin") == "rss":
            content = extract_article_content(item["link"], timeout)
            image_url = content.get("image")
            full_text = content.get("text")

        success = send_news_item(bot_token, chat_id, item, image_url, full_text)

        mark_seen(item["link"], seen_hashes)

        if success:
            sent_count += 1

        time.sleep(1.5)

    save_state(seen_hashes)
    print(f"=== تم إرسال {sent_count} من {len(items_to_send)} خبر بنجاح ===")


if __name__ == "__main__":
    main()
