import asyncio
import os
import re
import subprocess

from aiogram.types import FSInputFile, Message

import FFMpe
import Reply
import TrANs
import cAsh

CUT_PATTERN = re.compile(r"^(?P<a>[\d:]+)(?:\s*(?:[-/])\s*|\s+)(?P<b>[\d:]+)$")

MEDIA_MAP = {
    "document": Reply.MEDIA_DOCUMENT,
    "video": Reply.MEDIA_VIDEO,
    "video_note": Reply.MEDIA_VIDEO_NOTE,
    "voice": Reply.MEDIA_VOICE,
    "animation": Reply.BUTTON_STICKER,
}


def parse_time(value: str) -> float | None:
    parts = value.split(":")
    if not all(part.isdigit() for part in parts):
        return None
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return None


def parse_cut(text: str) -> tuple[float, float] | None:
    match = CUT_PATTERN.match(text)
    if not match:
        return None
    start = parse_time(match.group("a"))
    if start is None:
        return None
    if match.group("b") is None:
        return 0.0, start
    end = parse_time(match.group("b"))
    if end is None:
        return None
    return start, end


def _media_info(reply: Message) -> tuple[str, str, str] | None:
    for attr, label in MEDIA_MAP.items():
        candidate = getattr(reply, attr)
        if not candidate:
            continue
        if attr == "voice":
            return attr, label, "ogg"
        if attr in ("video_note", "animation"):
            return attr, label, "mp4"
        file_name = getattr(candidate, "file_name", None)
        if not file_name or "." not in file_name:
            return attr, label, None
        return attr, label, file_name.rsplit(".", 1)[-1]
    return None


async def start_cut(message: Message) -> None:
    reply = message.reply_to_message
    info = _media_info(reply)
    if info is None:
        return
    media_type, media_name, ext = info
    if ext is None:
        await message.reply(Reply.CUT_INVALID_TEMPLATE.format(media_name))
        return
    source = getattr(reply, media_type)
    cAsh.set_cut_wait(
        message.chat.id,
        message.from_user.id,
        message.message_thread_id,
        source.file_id,
        media_type,
        media_name,
        ext,
    )
    await message.reply(Reply.CUT_HINT)


async def execute_cut(message: Message) -> None:
    wait = cAsh.get_cut_wait(
        message.chat.id, message.from_user.id, message.message_thread_id
    )
    if wait is None:
        return
    parsed = parse_cut(message.text.strip())
    if parsed is None:
        await message.reply(
            Reply.CUT_INVALID_TEMPLATE.format(wait["media_name"])
        )
        return
    start, end = parsed
    if end <= start:
        await message.reply(
            Reply.CUT_INVALID_TEMPLATE.format(wait["media_name"])
        )
        return
    cAsh.clear_cut_wait(
        message.chat.id, message.from_user.id, message.message_thread_id
    )
    sent = await message.reply(Reply.START_MESSAGE)
    path = None
    try:
        target_dir = TrANs.build_dir(
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
        raw_name = f"{message.message_id}"
        raw_path = os.path.join(target_dir, raw_name)
        await message.bot.download(wait["file_id"], destination=raw_path)
        output = os.path.join(target_dir, f"{raw_name}_cut.{wait['ext']}")
        await asyncio.to_thread(
            FFMpe.cut_media, raw_path, output, start, end
        )
        file = FSInputFile(output)
        media_type = wait["media_type"]
        if media_type == "video":
            await message.reply_video(file)
        elif media_type == "video_note":
            await message.reply_video_note(file, length=640)
        elif media_type == "animation":
            await message.reply_animation(file)
        elif media_type == "voice":
            await message.reply_voice(file)
        else:
            await message.reply_document(file)
        await sent.delete()
        path = output
    except subprocess.CalledProcessError:
        await sent.edit_text(Reply.CUT_ERROR)
    except Exception:
        await sent.edit_text(Reply.ERROR_PROCESS)
    finally:
        if path is not None:
            TrANs.cleanup(
                path,
                message.chat.id,
                message.from_user.id,
                message.chat.type == "private",
            )
