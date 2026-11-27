import asyncio
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message

import Nookie
import Reply
import cAsh
import ediT

BOT_TOKEN = os.environ["BOT_TOKEN"]
BOOT_NOTICE = os.environ.get("boT_NoTice", "")
NOTICE_IDS = [int(uid) for uid in BOOT_NOTICE.split("/") if uid.strip().isdigit()]

router = Router()

LINK_PATTERN = r"https?://"
MENU_ROUTES = {
    "sticker": Nookie.send_sticker_menu,
    "videonote": Nookie.send_videonote_menu,
    "default": Nookie.send_default_menu,
    "language": Nookie.send_language_menu,
}
MODE_HANDLERS = {
    "sticker": Nookie.send_animation,
    "videonote": Nookie.send_video_note,
    "voice": Nookie.send_voice,
    "default": Nookie.send_default,
}


async def sync_bot_identity(bot: Bot) -> None:
    me = await bot.me()
    if me.username:
        cAsh.set_bot_username(me.username)


async def notify_startup(bot: Bot) -> None:
    for user_id in NOTICE_IDS:
        try:
            await bot.send_message(user_id, Reply.STARTUP_MESSAGE)
        except Exception:
            continue


@router.message(F.text == Reply.MENU_TRIGGER)
async def open_menu(message: Message) -> None:
    if not await Nookie.is_group_admin(message):
        return
    await Nookie.send_menu(message)


@router.message(F.text.regexp(LINK_PATTERN))
async def handle_link(message: Message) -> None:
    thread_id = message.message_thread_id
    handler = MODE_HANDLERS.get(cAsh.get_mode(message.chat.id, thread_id))
    if handler is None:
        return
    await handler(message, message.text)


@router.message(F.reply_to_message)
async def handle_reply_media(message: Message) -> None:
    if not message.text:
        return
    text = message.text.strip()
    reply = message.reply_to_message
    if not any(getattr(reply, attr, None) for attr in ediT.MEDIA_MAP):
        return
    if text.split(maxsplit=1)[0] in Reply.CUT_COMMANDS:
        await ediT.start_cut(message)
        return
    if text != Reply.VOICE:
        return
    await Nookie.extract_voice(message)


@router.message(F.text)
async def handle_text(message: Message) -> None:
    wait = cAsh.get_cut_wait(
        message.chat.id, message.from_user.id, message.message_thread_id
    )
    if wait is not None:
        await ediT.execute_cut(message)
        return
    if message.text == Reply.MENU_TRIGGER:
        return
    if message.text.startswith(("http://", "https://")):
        return
    if message.reply_to_message is not None:
        return
    thread_id = message.message_thread_id
    if cAsh.get_lang_active(message.chat.id, thread_id):
        await Nookie.translate_text(message)
        return
    await Nookie.send_text_reply(message, NOTICE_IDS)


@router.callback_query(F.data.startswith("menu:"))
async def handle_menu(callback: CallbackQuery) -> None:
    _, action, target, owner_id = callback.data.split(":")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return

    if action == "back":
        if target == "main":
            await Nookie.send_main_menu(callback)
        else:
            route = MENU_ROUTES.get(target)
            if route is not None:
                await route(callback)
    else:
        route = MENU_ROUTES.get(action)
        if route is not None:
            await route(callback)
        else:
            await Nookie.switch_mode(callback, action)
    await callback.answer()


@router.callback_query(F.data.regexp(r"^(sticker|videonote|default)_toggle:"))
async def handle_toggle(callback: CallbackQuery) -> None:
    _, owner_id = callback.data.split(":")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return

    mode = callback.data.split("_")[0]
    await Nookie.toggle_mode(callback, mode)

    if mode == "sticker":
        await Nookie.send_sticker_menu(callback)
    elif mode == "videonote":
        await Nookie.send_videonote_menu(callback)
    else:
        await Nookie.send_default_menu(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("default_delivery:"))
async def handle_delivery(callback: CallbackQuery) -> None:
    _, owner_id = callback.data.split(":")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return
    cAsh.toggle_delivery(
        callback.message.chat.id, callback.message.message_thread_id
    )
    await Nookie.send_default_menu(callback)
    await callback.answer()


@router.callback_query(F.data.regexp(r"^(sticker|videonote)_rotate:"))
async def handle_rotate(callback: CallbackQuery) -> None:
    mode, _, rest = callback.data.partition("_rotate:")
    value, owner_id = rest.split(":")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return
    await Nookie.toggle_rotation(callback, mode, value)
    await callback.answer()


@router.callback_query(F.data.regexp(r"^(sticker|videonote)_mirror:"))
async def handle_mirror(callback: CallbackQuery) -> None:
    mode, _, owner_id = callback.data.partition("_mirror:")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return
    await Nookie.toggle_mirror(callback, mode)
    await callback.answer()


@router.callback_query(F.data.regexp(r"^(sticker|videonote)_triple:"))
async def handle_triple(callback: CallbackQuery) -> None:
    mode, _, owner_id = callback.data.partition("_triple:")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return
    await Nookie.toggle_triple(callback, mode)
    await callback.answer()


@router.callback_query(F.data.startswith("language_set:"))
async def handle_language_set(callback: CallbackQuery) -> None:
    _, value, owner_id = callback.data.split(":")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return
    cAsh.switch_language(
        callback.message.chat.id,
        value,
        callback.message.message_thread_id,
    )
    await Nookie.send_language_menu(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("language_toggle:"))
async def handle_language_toggle(callback: CallbackQuery) -> None:
    _, owner_id = callback.data.split(":")
    if callback.from_user.id != int(owner_id):
        await callback.answer(Reply.ERROR_NOT_OWNER, show_alert=True)
        return
    cAsh.toggle_lang_active(
        callback.message.chat.id, callback.message.message_thread_id
    )
    await Nookie.send_language_menu(callback)
    await callback.answer()


async def main() -> None:
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    polling = asyncio.create_task(dp.start_polling(bot))
    await sync_bot_identity(bot)
    await notify_startup(bot)
    await polling


if __name__ == "__main__":
    asyncio.run(main())
