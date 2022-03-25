from __future__ import annotations

from typing import TypedDict

class Span(TypedDict):
    start : int
    end : int
    label : str
    rank : int