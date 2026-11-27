import os

from freetrans import Translator

BASE_DIR = "downloads"
UPPER_CHARS = set("ATFGUJNMLБИА")
LANG_CODES = {"eNG": "en", "rUS": "ru", "FrA": "fr"}


def _normalize(text: str) -> str:
    return "".join(
        ch.upper() if ch.upper() in UPPER_CHARS else ch.lower()
        for ch in text
    )


def has_format_chars(text: str) -> bool:
    return any(ch.upper() in UPPER_CHARS for ch in text)


def build_name(info: dict) -> str:
    parts = [
        info.get("uploader") or info.get("channel"),
        info.get("title"),
    ]
    name = " - ".join(_normalize(part) for part in parts if part)
    return name or info.get("id", "video")


def build_dir(chat_id: int, user_id: int, is_private: bool) -> str:
    if is_private:
        path = os.path.join(BASE_DIR, str(user_id))
    else:
        path = os.path.join(BASE_DIR, str(chat_id).lstrip("-"), str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def cleanup(file_path: str, chat_id: int, user_id: int, is_private: bool) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
    cleanup_empty(chat_id, user_id, is_private)


def cleanup_empty(chat_id: int, user_id: int, is_private: bool) -> None:
    if is_private:
        user_dir = os.path.join(BASE_DIR, str(user_id))
    else:
        user_dir = os.path.join(BASE_DIR, str(chat_id).lstrip("-"), str(user_id))
    if os.path.isdir(user_dir) and not os.listdir(user_dir):
        os.rmdir(user_dir)


async def translate(text: str, lang_key: str) -> str:
    dest = LANG_CODES.get(lang_key, "en")
    async with Translator() as translator:
        result = await translator.translate(text, dest=dest)
    return _normalize(result.text)
