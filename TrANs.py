import hashlib
import os
import shutil
import uuid

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


def id_feli(*parts: object) -> str:
    raw = "|".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_dir(chat_id: int, user_id: int, is_private: bool) -> str:
    if is_private:
        path = os.path.join(BASE_DIR, str(user_id))
    else:
        path = os.path.join(BASE_DIR, str(chat_id).lstrip("-"), str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def build_task_dir(chat_id: int, user_id: int, is_private: bool) -> str:
    base = build_dir(chat_id, user_id, is_private)
    task_dir = os.path.join(base, uuid.uuid4().hex)
    os.makedirs(task_dir, exist_ok=True)
    return task_dir


def cleanup_task_dir(
    task_dir: str | None, chat_id: int, user_id: int, is_private: bool
) -> None:
    if task_dir and os.path.isdir(task_dir):
        shutil.rmtree(task_dir, ignore_errors=True)
    cleanup_empty(chat_id, user_id, is_private)


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
