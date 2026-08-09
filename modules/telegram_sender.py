"""
إرسال الأخبار إلى بوت التلكرام:
رسالة أولى = صورة + عنوان مختصر
رسالة ثانية = رد على الأولى، فيها تفاصيل المقال الكامل
"""
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

MAX_CAPTION_LEN = 1000
MAX_MESSAGE_LEN = 4000


def _build_caption(item: dict) -> str:
    title = item.get("title", "خبر جديد")
    source = item.get("source", "")
    link = item.get("link", "")

    text = f"🛡️ <b>{title}</b>\n\n📰 المصدر: {source}\n🔗 {link}"
    if len(text) > MAX_CAPTION_LEN:
        text = text[:MAX_CAPTION_LEN - 3] + "..."
    return text


def _send_photo(bot_token, chat_id, image_url, caption):
    url = TELEGRAM_API.format(token=bot_token, method="sendPhoto")
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, data=payload, timeout=20)
        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return data["result"]["message_id"]
        return None
    except Exception:
        return None


def _send_text(bot_token, chat_id, text, reply_to_message_id=None):
    url = TELEGRAM_API.format(token=bot_token, method="sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    try:
        resp = requests.post(url, data=payload, timeout=20)
        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return data["result"]["message_id"]
        print(f"  [خطأ] فشل إرسال الرسالة: {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  [خطأ] استثناء عند إرسال الرسالة: {e}")
        return None


def send_news_item(bot_token: str, chat_id: str, item: dict, image_url: str | None, full_text: str | None = None) -> bool:
    caption = _build_caption(item)
    photo_msg_id = None

    if image_url:
        photo_msg_id = _send_photo(bot_token, chat_id, image_url, caption)

    if photo_msg_id is None:
        photo_msg_id = _send_text(bot_token, chat_id, caption)

    if photo_msg_id is None:
        return False

    if full_text:
        link = item.get("link", "")
        details = f"📄 <b>تفاصيل الخبر:</b>\n\n{full_text}"

        if len(details) > MAX_MESSAGE_LEN:
            details = details[:MAX_MESSAGE_LEN - 200] + f"\n\n... [النص مقتطع، الخبر أطول من حد تيليجرام]\n\n🔗 اقرأ الخبر كاملاً: {link}"

        _send_text(bot_token, chat_id, details, reply_to_message_id=photo_msg_id)

    return True
