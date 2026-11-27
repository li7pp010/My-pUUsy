import asyncio
import os
import subprocess

from aiogram.types import CallbackQuery, FSInputFile, Message

import FFMpe
import Reply
import TrANs
import bToN
import cAsh
import yTdLp

MEDIA_NAMES = {
    "document": Reply.MEDIA_DOCUMENT,
    "video": Reply.MEDIA_VIDEO,
    "video_note": Reply.MEDIA_VIDEO_NOTE,
    "voice": Reply.MEDIA_VOICE,
}


async def is_group_admin(message: Message) -> bool:
    if message.chat.type == "private":
        return True
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")


async def send_menu(message: Message) -> None:
    await message.reply(
        Reply.MENU_TEXT,
        reply_markup=bToN.main_menu(
            message.chat.id,
            message.from_user.id,
            cAsh.get_mode(message.chat.id, message.message_thread_id),
            message.message_thread_id,
        ),
    )


async def send_main_menu(callback: CallbackQuery) -> None:
    thread_id = callback.message.message_thread_id
    await callback.message.edit_text(
        Reply.MENU_TEXT,
        reply_markup=bToN.main_menu(
            callback.message.chat.id,
            callback.from_user.id,
            cAsh.get_mode(callback.message.chat.id, thread_id),
            thread_id,
        ),
    )


async def send_sticker_menu(callback: CallbackQuery) -> None:
    thread_id = callback.message.message_thread_id
    await callback.message.edit_text(
        Reply.SUB_MENU_TEXT.format(Reply.BUTTON_STICKER),
        reply_markup=bToN.sticker_menu(
            callback.message.chat.id, callback.from_user.id, thread_id
        ),
    )


async def send_videonote_menu(callback: CallbackQuery) -> None:
    thread_id = callback.message.message_thread_id
    await callback.message.edit_text(
        Reply.SUB_MENU_TEXT.format(Reply.BUTTON_VIDEONOTE),
        reply_markup=bToN.videonote_menu(
            callback.message.chat.id, callback.from_user.id, thread_id
        ),
    )


async def send_default_menu(callback: CallbackQuery) -> None:
    thread_id = callback.message.message_thread_id
    await callback.message.edit_text(
        Reply.SUB_MENU_TEXT.format(Reply.BUTTON_DEFAULT),
        reply_markup=bToN.default_menu(
            callback.message.chat.id, callback.from_user.id, thread_id
        ),
    )


async def send_language_menu(callback: CallbackQuery) -> None:
    thread_id = callback.message.message_thread_id
    await callback.message.edit_text(
        Reply.SUB_MENU_LANG_TEXT,
        reply_markup=bToN.language_menu(
            callback.message.chat.id, callback.from_user.id, thread_id
        ),
    )


async def toggle_mode(callback: CallbackQuery, mode: str) -> None:
    chat_id = callback.message.chat.id
    thread_id = callback.message.message_thread_id
    if cAsh.get_mode(chat_id, thread_id) == mode:
        cAsh.deactivate(chat_id, thread_id)
    else:
        cAsh.activate(chat_id, mode, thread_id)


async def switch_mode(callback: CallbackQuery, action: str) -> None:
    thread_id = callback.message.message_thread_id
    chat_id = callback.message.chat.id
    if cAsh.get_mode(chat_id, thread_id) == action:
        cAsh.deactivate(chat_id, thread_id)
        active = cAsh.get_mode(chat_id, thread_id)
    else:
        cAsh.activate(chat_id, action, thread_id)
        active = action
    await callback.message.edit_text(
        Reply.MENU_TEXT,
        reply_markup=bToN.main_menu(
            chat_id, callback.from_user.id, active, thread_id
        ),
    )


async def toggle_rotation(callback: CallbackQuery, mode: str, value: str) -> None:
    thread_id = callback.message.message_thread_id
    cAsh.toggle_rotation(callback.message.chat.id, mode, value, thread_id)
    if mode == "sticker":
        await send_sticker_menu(callback)
    else:
        await send_videonote_menu(callback)


async def toggle_mirror(callback: CallbackQuery, mode: str) -> None:
    thread_id = callback.message.message_thread_id
    cAsh.toggle_mirror(callback.message.chat.id, mode, thread_id)
    if mode == "sticker":
        await send_sticker_menu(callback)
    else:
        await send_videonote_menu(callback)


async def toggle_triple(callback: CallbackQuery, mode: str) -> None:
    thread_id = callback.message.message_thread_id
    cAsh.toggle_triple(callback.message.chat.id, mode, thread_id)
    if mode == "sticker":
        await send_sticker_menu(callback)
    else:
        await send_videonote_menu(callback)


async def send_animation(message: Message, url: str) -> None:
    sent = await message.reply(Reply.START_MESSAGE)
    thread_id = message.message_thread_id
    task_dir = None
    try:
        task_dir = TrANs.build_task_dir(
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
        path = await yTdLp.process_animation(
            url,
            task_dir,
            cAsh.get_rotation(message.chat.id, "sticker", thread_id),
            cAsh.get_mirror(message.chat.id, "sticker", thread_id),
            cAsh.get_triple(message.chat.id, "sticker", thread_id),
        )
        await message.reply_animation(FSInputFile(path))
        await sent.delete()
    except yTdLp.DownloadError:
        await sent.edit_text(Reply.ERROR_DOWNLOAD)
    except Exception:
        await sent.edit_text(Reply.ERROR_PROCESS)
    finally:
        TrANs.cleanup_task_dir(
            task_dir, message.chat.id, message.from_user.id,
            message.chat.type == "private",
        )


async def send_video_note(message: Message, url: str) -> None:
    sent = await message.reply(Reply.START_MESSAGE)
    thread_id = message.message_thread_id
    task_dir = None
    try:
        task_dir = TrANs.build_task_dir(
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
        path = await yTdLp.process_video_note(
            url,
            task_dir,
            cAsh.get_rotation(message.chat.id, "videonote", thread_id),
            cAsh.get_mirror(message.chat.id, "videonote", thread_id),
            cAsh.get_triple(message.chat.id, "videonote", thread_id),
        )
        await message.reply_video_note(FSInputFile(path), length=640)
        await sent.delete()
    except yTdLp.DownloadError:
        await sent.edit_text(Reply.ERROR_DOWNLOAD)
    except Exception:
        await sent.edit_text(Reply.ERROR_PROCESS)
    finally:
        TrANs.cleanup_task_dir(
            task_dir, message.chat.id, message.from_user.id,
            message.chat.type == "private",
        )


async def send_voice(message: Message, url: str) -> None:
    sent = await message.reply(Reply.START_MESSAGE)
    task_dir = None
    try:
        task_dir = TrANs.build_task_dir(
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
        path = await yTdLp.process_voice(url, task_dir)
        await message.reply_voice(FSInputFile(path))
        await sent.delete()
    except yTdLp.DownloadError:
        await sent.edit_text(Reply.ERROR_DOWNLOAD)
    except Exception:
        await sent.edit_text(Reply.ERROR_PROCESS)
    finally:
        TrANs.cleanup_task_dir(
            task_dir, message.chat.id, message.from_user.id,
            message.chat.type == "private",
        )


async def send_default(message: Message, url: str) -> None:
    sent = await message.reply(Reply.START_MESSAGE)
    task_dir = None
    try:
        task_dir = TrANs.build_task_dir(
            message.chat.id,
            message.from_user.id,
            message.chat.type == "private",
        )
        path = await yTdLp.process_default(url, task_dir)
        await message.reply_document(FSInputFile(path))
        await sent.delete()
    except yTdLp.DownloadError:
        await sent.edit_text(Reply.ERROR_DOWNLOAD)
    except Exception:
        await sent.edit_text(Reply.ERROR_PROCESS)
    finally:
        TrANs.cleanup_task_dir(
            task_dir, message.chat.id, message.from_user.id,
            message.chat.type == "private",
        )


async def translate_text(message: Message) -> None:
    thread_id = message.message_thread_id
    if TrANs.has_format_chars(message.text):
        await message.reply(TrANs._normalize(message.text))
        return
    lang = cAsh.get_language(message.chat.id, thread_id)
    try:
        translated = await TrANs.translate(message.text, lang)
    except Exception:
        return
    await message.reply(translated)


async def send_text_reply(message: Message, developer_ids: list[int]) -> None:
    thread_id = message.message_thread_id
    text = cAsh.next_text_reply(message.chat.id, thread_id)
    developer = cAsh.next_developer(
        message.chat.id, developer_ids, bToN.DEVELOPER_COLORS, thread_id
    )
    markup = None
    if developer is not None:
        name, dev_id, color = developer
        markup = bToN.developer_button(name, dev_id, color)
    await message.reply(text, reply_markup=markup)


async def extract_voice(message: Message) -> None:
    reply = message.reply_to_message
    source = None
    name = None
    for attr, label in MEDIA_NAMES.items():
        candidate = getattr(reply, attr)
        if candidate:
            source = candidate
            name = label
            break
    if source is None:
        return
    sent = await message.reply(Reply.VOICE_REPLY_TEMPLATE.format(name))
    task_dir = None
    try:
        task_dir = TrANs.build_task_dir(
            message.chat.id, message.from_user.id,
            message.chat.type == "private",
        )
        raw_id = TrANs.id_feli("reply_voice_raw", source.file_id)
        raw_path = os.path.join(task_dir, raw_id)
        await message.bot.download(source, destination=raw_path)
        out_id = TrANs.id_feli("reply_voice", source.file_id, "ogg")
        output = os.path.join(task_dir, f"{out_id}.ogg")
        await asyncio.to_thread(FFMpe.to_voice, raw_path, output)
        await message.reply_voice(FSInputFile(output))
        await sent.delete()
    except subprocess.CalledProcessError:
        await sent.edit_text(Reply.NO_AUDIO_TEMPLATE.format(name))
    except Exception:
        await sent.edit_text(Reply.ERROR_PROCESS)
    finally:
        TrANs.cleanup_task_dir(
            task_dir, message.chat.id, message.from_user.id,
            message.chat.type == "private",
        )
