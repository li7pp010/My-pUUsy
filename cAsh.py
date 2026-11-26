_states: dict[int, dict[str, str]] = {}
_delivery: dict[int, str] = {}
_rotation: dict[tuple[int, str], str] = {}
_mirror: dict[tuple[int, str], bool] = {}
_triple: dict[tuple[int, str], bool] = {}
_language: dict[int, str] = {}
_reply_index: dict[int, int] = {}
_dev_name_index: dict[int, int] = {}
_dev_id_index: dict[int, int] = {}
_dev_color_index: dict[int, int] = {}

DEFAULT_ACTIVE = "sticker"
DEFAULT_PREVIOUS = "voice"
DEFAULT_DELIVERY = "document"
DEFAULT_ROTATION = "none"
DEFAULT_MIRROR = False
DEFAULT_TRIPLE = False
DEFAULT_LANGUAGE = "eNG"
LANGUAGES = ("eNG", "rUS", "FrA")


def _state(chat_id: int) -> dict[str, str]:
    return _states.setdefault(
        chat_id, {"current": DEFAULT_ACTIVE, "previous": DEFAULT_PREVIOUS}
    )


def get_mode(chat_id: int) -> str:
    return _state(chat_id)["current"]


def activate(chat_id: int, mode: str) -> None:
    state = _state(chat_id)
    if state["current"] != mode:
        state["previous"] = state["current"]
        state["current"] = mode


def deactivate(chat_id: int) -> None:
    state = _state(chat_id)
    state["current"] = state["previous"]


def get_delivery(chat_id: int) -> str:
    return _delivery.get(chat_id, DEFAULT_DELIVERY)


def toggle_delivery(chat_id: int) -> None:
    _delivery[chat_id] = (
        "video" if get_delivery(chat_id) == "document" else "document"
    )


def get_rotation(chat_id: int, mode: str) -> str:
    return _rotation.get((chat_id, mode), DEFAULT_ROTATION)


def toggle_rotation(chat_id: int, mode: str, value: str) -> None:
    current = get_rotation(chat_id, mode)
    _rotation[(chat_id, mode)] = "none" if current == value else value


def get_mirror(chat_id: int, mode: str) -> bool:
    return _mirror.get((chat_id, mode), DEFAULT_MIRROR)


def toggle_mirror(chat_id: int, mode: str) -> None:
    _mirror[(chat_id, mode)] = not get_mirror(chat_id, mode)


def get_triple(chat_id: int, mode: str) -> bool:
    return _triple.get((chat_id, mode), DEFAULT_TRIPLE)


def toggle_triple(chat_id: int, mode: str) -> None:
    _triple[(chat_id, mode)] = not get_triple(chat_id, mode)


def get_language(chat_id: int) -> str:
    return _language.get(chat_id, DEFAULT_LANGUAGE)


def set_language(chat_id: int, value: str) -> None:
    _language[chat_id] = value


def switch_language(chat_id: int, value: str) -> None:
    current = get_language(chat_id)
    if value != current:
        _language[chat_id] = value
        return
    index = LANGUAGES.index(value) if value in LANGUAGES else -1
    next_index = (index + 1) % len(LANGUAGES)
    _language[chat_id] = LANGUAGES[next_index]


def next_text_reply(chat_id: int) -> str:
    from Reply import TEXT_REPLIES

    index = _reply_index.get(chat_id, 0)
    reply = TEXT_REPLIES[index % len(TEXT_REPLIES)]
    _reply_index[chat_id] = (index + 1) % len(TEXT_REPLIES)
    return reply


def next_developer(chat_id: int, ids: list[int]) -> tuple[str, int, str] | None:
    from Reply import DEVELOPER_COLORS, DEVELOPER_NAMES

    if not ids:
        return None
    name_index = _dev_name_index.get(chat_id, 0)
    id_index = _dev_id_index.get(chat_id, 0)
    color_index = _dev_color_index.get(chat_id, 0)
    name = DEVELOPER_NAMES[name_index % len(DEVELOPER_NAMES)]
    dev_id = ids[id_index % len(ids)]
    color = DEVELOPER_COLORS[color_index % len(DEVELOPER_COLORS)]
    _dev_name_index[chat_id] = (name_index + 1) % len(DEVELOPER_NAMES)
    _dev_id_index[chat_id] = (id_index + 1) % len(ids)
    _dev_color_index[chat_id] = (color_index + 1) % len(DEVELOPER_COLORS)
    return name, dev_id, color