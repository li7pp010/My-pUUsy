_states: dict[tuple[int, int], dict[str, str]] = {}  
_delivery: dict[tuple[int, int], str] = {}  
_rotation: dict[tuple[int, int, str], str] = {}  
_mirror: dict[tuple[int, int, str], bool] = {}  
_triple: dict[tuple[int, int, str], bool] = {}  
_language: dict[tuple[int, int], str] = {}  
_lang_active: dict[tuple[int, int], bool] = {}  
_reply_index: dict[tuple[int, int], int] = {}  
_dev_name_index: dict[tuple[int, int], int] = {}  
_dev_id_index: dict[tuple[int, int], int] = {}  
_dev_color_index: dict[tuple[int, int], int] = {}  
  
DEFAULT_ACTIVE = "sticker"  
DEFAULT_PREVIOUS = "voice"  
DEFAULT_DELIVERY = "document"  
DEFAULT_ROTATION = "none"  
DEFAULT_MIRROR = False  
DEFAULT_TRIPLE = False  
DEFAULT_LANGUAGE = "eNG"  
DEFAULT_LANG_ACTIVE = False  
LANGUAGES = ("eNG", "rUS", "FrA")  
  
  
def _thread(thread_id: int | None) -> int:  
    return thread_id if thread_id is not None else 0  
  
  
def _state(chat_id: int, thread_id: int | None = None) -> dict[str, str]:  
    key = (chat_id, _thread(thread_id))  
    return _states.setdefault(  
        key, {"current": DEFAULT_ACTIVE, "previous": DEFAULT_PREVIOUS}  
    )  
  
  
def get_mode(chat_id: int, thread_id: int | None = None) -> str:  
    return _state(chat_id, thread_id)["current"]  
  
  
def activate(chat_id: int, mode: str, thread_id: int | None = None) -> None:  
    state = _state(chat_id, thread_id)  
    if state["current"] != mode:  
        state["previous"] = state["current"]  
        state["current"] = mode  
  
  
def deactivate(chat_id: int, thread_id: int | None = None) -> None:  
    state = _state(chat_id, thread_id)  
    state["current"] = state["previous"]  
  
  
def get_delivery(chat_id: int, thread_id: int | None = None) -> str:  
    return _delivery.get((chat_id, _thread(thread_id)), DEFAULT_DELIVERY)  
  
  
def toggle_delivery(chat_id: int, thread_id: int | None = None) -> None:  
    key = (chat_id, _thread(thread_id))  
    _delivery[key] = (  
        "video" if _delivery.get(key, DEFAULT_DELIVERY) == "document" else "document"  
    )  
  
  
def get_rotation(chat_id: int, mode: str, thread_id: int | None = None) -> str:  
    return _rotation.get((chat_id, _thread(thread_id), mode), DEFAULT_ROTATION)  
  
  
def toggle_rotation(  
    chat_id: int, mode: str, value: str, thread_id: int | None = None  
) -> None:  
    key = (chat_id, _thread(thread_id), mode)  
    current = _rotation.get(key, DEFAULT_ROTATION)  
    _rotation[key] = "none" if current == value else value  
  
  
def get_mirror(chat_id: int, mode: str, thread_id: int | None = None) -> bool:  
    return _mirror.get((chat_id, _thread(thread_id), mode), DEFAULT_MIRROR)  
  
  
def toggle_mirror(chat_id: int, mode: str, thread_id: int | None = None) -> None:  
    key = (chat_id, _thread(thread_id), mode)  
    _mirror[key] = not _mirror.get(key, DEFAULT_MIRROR)  
  
  
def get_triple(chat_id: int, mode: str, thread_id: int | None = None) -> bool:  
    return _triple.get((chat_id, _thread(thread_id), mode), DEFAULT_TRIPLE)  
  
  
def toggle_triple(chat_id: int, mode: str, thread_id: int | None = None) -> None:  
    key = (chat_id, _thread(thread_id), mode)  
    _triple[key] = not _triple.get(key, DEFAULT_TRIPLE)  
  
  
def get_language(chat_id: int, thread_id: int | None = None) -> str:  
    return _language.get((chat_id, _thread(thread_id)), DEFAULT_LANGUAGE)  
  
  
def set_language(chat_id: int, value: str, thread_id: int | None = None) -> None:  
    _language[(chat_id, _thread(thread_id))] = value  
  
  
def switch_language(chat_id: int, value: str, thread_id: int | None = None) -> None:  
    current = get_language(chat_id, thread_id)  
    if value != current:  
        _language[(chat_id, _thread(thread_id))] = value  
        return  
    index = LANGUAGES.index(value) if value in LANGUAGES else -1  
    next_index = (index + 1) % len(LANGUAGES)  
    _language[(chat_id, _thread(thread_id))] = LANGUAGES[next_index]  
  
  
def get_lang_active(chat_id: int, thread_id: int | None = None) -> bool:  
    return _lang_active.get((chat_id, _thread(thread_id)), DEFAULT_LANG_ACTIVE)  
  
  
def toggle_lang_active(chat_id: int, thread_id: int | None = None) -> None:  
    key = (chat_id, _thread(thread_id))  
    _lang_active[key] = not _lang_active.get(key, DEFAULT_LANG_ACTIVE)  
  
  
def next_text_reply(chat_id: int, thread_id: int | None = None) -> str:  
    from Reply import TEXT_REPLIES  
  
    key = (chat_id, _thread(thread_id))  
    index = _reply_index.get(key, 0)  
    reply = TEXT_REPLIES[index % len(TEXT_REPLIES)]  
    _reply_index[key] = (index + 1) % len(TEXT_REPLIES)  
    return reply  
  
  
def next_developer(  
    chat_id: int, ids: list[int], thread_id: int | None = None  
) -> tuple[str, int, str] | None:  
    from Reply import DEVELOPER_COLORS, DEVELOPER_NAMES  
  
    if not ids:  
        return None  
    key = (chat_id, _thread(thread_id))  
    name_index = _dev_name_index.get(key, 0)  
    id_index = _dev_id_index.get(key, 0)  
    color_index = _dev_color_index.get(key, 0)  
    name = DEVELOPER_NAMES[name_index % len(DEVELOPER_NAMES)]  
    dev_id = ids[id_index % len(ids)]  
    color = DEVELOPER_COLORS[color_index % len(DEVELOPER_COLORS)]  
    _dev_name_index[key] = (name_index + 1) % len(DEVELOPER_NAMES)  
    _dev_id_index[key] = (id_index + 1) % len(ids)  
    _dev_color_index[key] = (color_index + 1) % len(DEVELOPER_COLORS)  
    return name, dev_id, color
