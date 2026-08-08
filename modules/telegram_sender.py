"""
إرسال الأخبار إلى بوت التلكرام (صورة + نص، أو نص فقط لو ما فيه صورة).
"""
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

# حدود تيليجرام: caption حده الأقصى 1024 حرف، الرسالة النصية 4096
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


def send_news_item(bot_token: str, chat_id: str, item: dict, image_url: str | None) -> bool:
    """يرسل خبر واحد للتلكرام. يرجع True لو نجح الإرسال."""
    caption = _build_caption(item)

    if image_url:
        # نحاول أول شي نرسلها كصورة مع تعليق
        url = TELEGRAM_API.format(token=bot_token, method="sendPhoto")
        payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML",
        }
        try:
            resp = requests.post(url, data=payload, timeout=20)
            if resp.status_code == 200 and resp.json().get("ok"):
                return True
            else:
                print(f"  [تحذير] فشل إرسال الصورة، بنجرب نص فقط. رد تيليجرام: {resp.text[:200]}")
        except Exception as e:
            print(f"  [تحذير] خطأ بإرسال الصورة: {e}")

    # لو ما فيه صورة أو فشل إرسالها، نرسل رسالة نصية عادية
    url = TELEGRAM_API.format(token=bot_token, method="sendMessage")
    text = caption if len(caption) <= MAX_MESSAGE_LEN else caption[:MAX_MESSAGE_LEN - 3] + "..."
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, data=payload, timeout=20)
        if resp.status_code == 200 and resp.json().get("ok"):
            return True
        print(f"  [خطأ] فشل إرسال الرسالة النصية أيضاً: {resp.text[:200]}")
        return False
    except Exception as e:
        print(f"  [خطأ] استثناء عند إرسال الرسالة: {e}")
        return False
