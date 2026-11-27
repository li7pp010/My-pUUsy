from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import Reply
import cAsh

COLOR_PRIMARY = "primary"
COLOR_DANGER = "danger"
COLOR_SUCCESS = "success"
DEVELOPER_COLORS = (COLOR_DANGER, COLOR_SUCCESS, COLOR_PRIMARY)


def _promote_url() -> str:
    username = cAsh.get_bot_username()
    return f"https://t.me/{username}?startgroup=true" if username else "https://t.me/"


def _promote_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=Reply.BUTTON_PROMOTE,
        url=_promote_url(),
        style=COLOR_SUCCESS,
    )


def _back_button(user_id: int, parent: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=Reply.BUTTON_BACK,
        callback_data=f"menu:back:{parent}:{user_id}",
        style=COLOR_SUCCESS,
    )


def _transform_buttons(
    chat_id: int, user_id: int, mode: str, thread_id: int | None = None
) -> list[list[InlineKeyboardButton]]:
    rotation = cAsh.get_rotation(chat_id, mode, thread_id)
    mirror = cAsh.get_mirror(chat_id, mode, thread_id)
    triple = cAsh.get_triple(chat_id, mode, thread_id)
    return [
        [
            InlineKeyboardButton(
                text=Reply.BUTTON_ROTATE_RIGHT,
                callback_data=f"{mode}_rotate:right:{user_id}",
                style=COLOR_PRIMARY if rotation == "right" else COLOR_DANGER,
            ),
            InlineKeyboardButton(
                text=Reply.BUTTON_ROTATE_LEFT,
                callback_data=f"{mode}_rotate:left:{user_id}",
                style=COLOR_PRIMARY if rotation == "left" else COLOR_DANGER,
            ),
            InlineKeyboardButton(
                text=Reply.BUTTON_TRIPLE,
                callback_data=f"{mode}_triple:{user_id}",
                style=COLOR_PRIMARY if triple else COLOR_DANGER,
            ),
        ],
        [
            InlineKeyboardButton(
                text=Reply.BUTTON_MIRROR,
                callback_data=f"{mode}_mirror:{user_id}",
                style=COLOR_PRIMARY if mirror else COLOR_DANGER,
            )
        ],
    ]


def _mode_button(
    text: str, key: str, user_id: int, active: str
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=f"menu:{key}:main:{user_id}",
        style=COLOR_PRIMARY if key == active else COLOR_DANGER,
    )


def main_menu(
    chat_id: int, user_id: int, active: str, thread_id: int | None = None
) -> InlineKeyboardMarkup:
    lang_button = InlineKeyboardButton(
        text=Reply.BUTTON_LANGUAGE,
        callback_data=f"menu:language:main:{user_id}",
        style=COLOR_SUCCESS if cAsh.get_lang_active(chat_id, thread_id) else COLOR_DANGER,
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _mode_button(Reply.BUTTON_STICKER, "sticker", user_id, active),
                _mode_button(Reply.VOICE, "voice", user_id, active),
                _mode_button(Reply.BUTTON_DEFAULT, "default", user_id, active),
            ],
            [_promote_button()],
            [
                _mode_button(Reply.BUTTON_VIDEONOTE, "videonote", user_id, active),
                lang_button,
            ],
        ]
    )


def sticker_menu(
    chat_id: int, user_id: int, thread_id: int | None = None
) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id, thread_id) == "sticker"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = COLOR_PRIMARY if active else COLOR_DANGER
    rows = [
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"sticker_toggle:{user_id}",
                style=style,
            )
        ],
    ]
    rows += _transform_buttons(chat_id, user_id, "sticker", thread_id)
    rows.append([_back_button(user_id, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def videonote_menu(
    chat_id: int, user_id: int, thread_id: int | None = None
) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id, thread_id) == "videonote"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = COLOR_PRIMARY if active else COLOR_DANGER
    rows = [
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"videonote_toggle:{user_id}",
                style=style,
            )
        ],
    ]
    rows += _transform_buttons(chat_id, user_id, "videonote", thread_id)
    rows.append([_back_button(user_id, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def default_menu(
    chat_id: int, user_id: int, thread_id: int | None = None
) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id, thread_id) == "default"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = COLOR_PRIMARY if active else COLOR_DANGER
    delivery = cAsh.get_delivery(chat_id, thread_id)
    delivery_label = (
        Reply.BUTTON_VIDEO if delivery == "video" else Reply.BUTTON_DOCUMENT
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"default_toggle:{user_id}",
                    style=style,
                )
            ],
            [
                InlineKeyboardButton(
                    text=delivery_label,
                    callback_data=f"default_delivery:{user_id}",
                    style=COLOR_PRIMARY,
                )
            ],
            [_back_button(user_id, "main")],
        ]
    )


def language_menu(
    chat_id: int, user_id: int, thread_id: int | None = None
) -> InlineKeyboardMarkup:
    active = cAsh.get_lang_active(chat_id, thread_id)
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = COLOR_PRIMARY if active else COLOR_DANGER
    lang = cAsh.get_language(chat_id, thread_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Reply.BUTTON_LANG_EN,
                    callback_data=f"language_set:eNG:{user_id}",
                    style=COLOR_PRIMARY if lang == "eNG" else COLOR_DANGER,
                ),
                InlineKeyboardButton(
                    text=Reply.BUTTON_LANG_RU,
                    callback_data=f"language_set:rUS:{user_id}",
                    style=COLOR_PRIMARY if lang == "rUS" else COLOR_DANGER,
                ),
                InlineKeyboardButton(
                    text=Reply.BUTTON_LANG_FR,
                    callback_data=f"language_set:FrA:{user_id}",
                    style=COLOR_PRIMARY if lang == "FrA" else COLOR_DANGER,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"language_toggle:{user_id}",
                    style=style,
                )
            ],
            [_back_button(user_id, "main")],
        ]
    )


def developer_button(name: str, dev_id: int, color: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=name,
                    url=f"tg://user?id={dev_id}",
                    style=color,
                )
            ]
        ]
    )
