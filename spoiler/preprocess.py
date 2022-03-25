import html
import re
from typing import Iterable
from unicodedata import normalize as normalize_unicode

_user_pattern = re.compile(r"@\w+")
_tag_pattern = re.compile(r"#\w+")
_url_pattern = re.compile(r"https?://t.co/\w+")


def normalize(text: str) -> str:
    text = normalize_unicode("NFKC", text)
    text = html.unescape(text)
    text = _user_pattern.sub(" @USER ", text)
    text = _tag_pattern.sub(" #TAG ", text)
    text = _url_pattern.sub(" URL ", text)
    return " ".join(text.split())


_strip = " ()*"


def _clean(text: str):
    text = text.strip(_strip)
    return text


_markers = (
    "alerta de spoiler",
    "alerta spoiler",
    "spoiler alert",
    "spoiler",
)
_spoiler_pattern = re.compile(
    r"🚨*\s*(" + "|".join(map(re.escape, _markers)) + r")\s*🚨*\s*:"
)


def get_spoiler_text(text: str) -> Iterable[str]:
    l_text = text.lower()
    for match in _spoiler_pattern.finditer(l_text):
        _, end_index = match.span()
        right = _clean(text[end_index:])
        if right:
            yield right
        return
