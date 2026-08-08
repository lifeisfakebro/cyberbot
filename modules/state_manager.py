"""
إدارة حالة البوت: يخزن هاشات الأخبار اللي تم إرسالها من قبل
عشان ما يعيد إرسال نفس الخبر مرتين.
"""
import json
import hashlib
import os

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state", "seen_items.json")

# أقصى عدد هاشات نحتفظ فيها عشان الملف ما يكبر بدون نهاية
MAX_STORED_HASHES = 3000


def _hash_item(unique_string: str) -> str:
    """يحول أي نص (رابط الخبر مثلاً) إلى هاش ثابت وقصير."""
    return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()


def load_state() -> set:
    """يقرأ قائمة الهاشات المخزنة من ملف الحالة."""
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_hashes", []))
    except (json.JSONDecodeError, OSError):
        # لو الملف تالف أو فاضي، نبدأ بحالة نظيفة بدل ما نوقف البوت
        return set()


def save_state(seen_hashes: set) -> None:
    """يحفظ قائمة الهاشات، مع الاحتفاظ بآخر MAX_STORED_HASHES فقط."""
    hashes_list = list(seen_hashes)
    if len(hashes_list) > MAX_STORED_HASHES:
        hashes_list = hashes_list[-MAX_STORED_HASHES:]

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"seen_hashes": hashes_list}, f, ensure_ascii=False, indent=2)


def is_new(unique_string: str, seen_hashes: set) -> bool:
    """يتحقق إذا كان هذا الخبر جديد (ما تم إرساله من قبل)."""
    return _hash_item(unique_string) not in seen_hashes


def mark_seen(unique_string: str, seen_hashes: set) -> None:
    """يضيف الخبر لقائمة (تم إرسالها) بدون ما يحفظ الملف فوراً."""
    seen_hashes.add(_hash_item(unique_string))
