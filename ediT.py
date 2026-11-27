import asyncio
import os
import re
import subprocess

from aiogram.types import FSInputFile, Message

import FFMpe
import Reply
import TrANs
import cAsh

TIME_TOKEN = r"[\d:]+(?:\.\d+)?"
CUT_PATTERN = re.compile(
    rf"^(?P<a>{TIME_TOKEN})(?:(?:\s*(?:[-/])\s*|\s+)(?P<b>{TIME_TOKEN}))?$"
)


def parse_time(value: str) -> float | None:
    if "." in value:
        sec_part, ms_part = value.split(".", 1)
        if not ms_part.isdigit():
            return None
        ms_val = int(ms_part)
        if ms_val < 0 or ms_val > 60:
            return None
        extra_sec = 1.0 if ms_val == 60 else ms_val / 1000.0
    else:
        sec_part = value
        extra_sec = 0.0

    parts = sec_part.split(":")
    if not all(part.isdigit() for part in parts):
        return None

    if len(parts) == 1:
        sec = int(parts[0])
        if sec < 0 or sec > 60:
            return None
        total = float(sec) + extra_sec
    elif len(parts) == 2:
        mins = int(parts[0])
        sec = int(parts[1])
        if mins < 0 or mins > 60 or sec < 0 or sec > 60:
            return None
        total = float(mins) * 60.0 + float(sec) + extra_sec
    elif len(parts) == 3:
        hours = int(parts[0])
        mins = int(parts[1])
        sec = int(parts[2])
        if hours < 0 or hours > 24 or mins < 0 or mins > 60 or sec < 0 or sec > 60:
            return None
        total = float(hours) * 3600.0 + float(mins) * 60.0 + float(sec) + extra_sec
    else:
        return None

    return total


def parse_cut(text: str) -> tuple[float, float] | None:
    match = CUT_PATTERN.match(text)
    if not match:
        return None
    first = parse_time(match.group("a"))
    if first is None:
        return None
    if match.group("b") is None:
        if first <= 0:
            return None
        return 0.0, first
    end = parse_time(match.group("b"))
    if end is None:
        return None
    return first, end


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
    media_label = (
        Reply.BUTTON_STICKER
        if wait["media_type"] == "animation"
        else wait["media_name"]
    )
    parsed = parse_cut(message.text.strip())
    if parsed is None:
        await message.reply(
            Reply.CUT_INVALID_TEMPLATE.format(media_label)
        )
        return
    start, end = parsed
    if end <= start:
        await message.reply(
            Reply.CUT_INVALID_TEMPLATE.format(media_label)
        )
        return
    cAsh.clear_cut_wait(
        message.chat.id, message.from_user.id, message.message_thread_id
    )
    task_dir = None
    try:
        task_dir = TrANs.build_task_dir(
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
        media_type = wait["media_type"]
        ext = wait["ext"]
        raw_id = TrANs.id_feli("cut_raw", media_type, wait["file_id"], ext)
        raw_path = os.path.join(task_dir, f"{raw_id}.{ext}")
        await message.bot.download(wait["file_id"], destination=raw_path)
        out_id = TrANs.id_feli("cut", media_type, wait["file_id"], start, end, ext)
        output = os.path.join(task_dir, f"{out_id}.{ext}")
        cut_fn = FFMpe.cut_animation if media_type == "animation" else FFMpe.cut_media
        await asyncio.to_thread(
            cut_fn, raw_path, output, start, end
        )
        file = FSInputFile(output)
        if media_type == "video":
            await message.reply_video(file)
        elif media_type == "video_note":
            await message.reply_video_note(file, length=640)
        elif media_type == "animation":
            await message.reply_sticker(file)
        elif media_type == "voice":
            await message.reply_voice(file)
        else:
            await message.reply_document(file)
    except subprocess.CalledProcessError:
        await message.reply(Reply.CUT_INVALID_TEMPLATE.format(media_label))
    except Exception:
        await message.reply(Reply.ERROR_PROCESS)
    finally:
        TrANs.cleanup_task_dir(
            task_dir,
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
