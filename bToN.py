from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import Reply
import cAsh

BUTTONS = (
    (Reply.BUTTON_STICKER, "sticker"),
    (Reply.BUTTON_VIDEONOTE, "videonote"),
    (Reply.VOICE, "voice"),
    (Reply.BUTTON_DEFAULT, "default"),
)


def _back_button(user_id: int, parent: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=Reply.BUTTON_BACK,
        callback_data=f"menu:back:{parent}:{user_id}",
        style="success",
    )


def _transform_buttons(
    chat_id: int, user_id: int, mode: str
) -> list[list[InlineKeyboardButton]]:
    rotation = cAsh.get_rotation(chat_id, mode)
    mirror = cAsh.get_mirror(chat_id, mode)
    triple = cAsh.get_triple(chat_id, mode)
    return [
        [
            InlineKeyboardButton(
                text=Reply.BUTTON_ROTATE_RIGHT,
                callback_data=f"{mode}_rotate:right:{user_id}",
                style="primary" if rotation == "right" else "danger",
            ),
            InlineKeyboardButton(
                text=Reply.BUTTON_ROTATE_LEFT,
                callback_data=f"{mode}_rotate:left:{user_id}",
                style="primary" if rotation == "left" else "danger",
            ),
            InlineKeyboardButton(
                text=Reply.BUTTON_TRIPLE,
                callback_data=f"{mode}_triple:{user_id}",
                style="primary" if triple else "danger",
            ),
        ],
        [
            InlineKeyboardButton(
                text=Reply.BUTTON_MIRROR,
                callback_data=f"{mode}_mirror:{user_id}",
                style="primary" if mirror else "danger",
            )
        ],
    ]


def main_menu(user_id: int, active: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, key in BUTTONS:
        builder.button(
            text=label,
            callback_data=f"menu:{key}:main:{user_id}",
            style="primary" if key == active else "danger",
        )
    builder.button(
        text=Reply.BUTTON_LANGUAGE,
        callback_data=f"menu:language:main:{user_id}",
        style="primary" if active == "language" else "danger",
    )
    builder.adjust(3, 2)
    return builder.as_markup()


def sticker_menu(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id) == "sticker"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = "primary" if active else "danger"
    rows = [
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"sticker_toggle:{user_id}",
                style=style,
            )
        ],
    ]
    rows += _transform_buttons(chat_id, user_id, "sticker")
    rows.append([_back_button(user_id, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def videonote_menu(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id) == "videonote"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = "primary" if active else "danger"
    rows = [
        [
            InlineKeyboardButton(
                text=label,
                callback_data=f"videonote_toggle:{user_id}",
                style=style,
            )
        ],
    ]
    rows += _transform_buttons(chat_id, user_id, "videonote")
    rows.append([_back_button(user_id, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def default_menu(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id) == "default"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = "primary" if active else "danger"
    delivery = cAsh.get_delivery(chat_id)
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
                    style="primary",
                )
            ],
            [_back_button(user_id, "main")],
        ]
    )


def language_menu(chat_id: int, user_id: int) -> InlineKeyboardMarkup:
    active = cAsh.get_mode(chat_id) == "language"
    label = Reply.BUTTON_DEACTIVATE if active else Reply.BUTTON_ACTIVATE
    style = "primary" if active else "danger"
    lang = cAsh.get_language(chat_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Reply.BUTTON_LANG_EN,
                    callback_data=f"language_set:eNG:{user_id}",
                    style="primary" if lang == "eNG" else "danger",
                ),
                InlineKeyboardButton(
                    text=Reply.BUTTON_LANG_RU,
                    callback_data=f"language_set:rUS:{user_id}",
                    style="primary" if lang == "rUS" else "danger",
                ),
                InlineKeyboardButton(
                    text=Reply.BUTTON_LANG_FR,
                    callback_data=f"language_set:FrA:{user_id}",
                    style="primary" if lang == "FrA" else "danger",
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