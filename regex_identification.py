from __future__ import annotations

from typing import List, Optional, TypedDict
from meta import Span
from sensitive_identifier import SensitiveIdentifier
import csv

from formatters import Registry

# This file will contain the methods for the identification of the regular sensitive data

import re


class Pattern(TypedDict):
    label : str
    reg : str
    rank : int

class RegexIdentifier(SensitiveIdentifier):
    def __init__(self, model_csv : str, label_list: Optional[List[str]] = None) -> None:
        super().__init__(label_list)
        self._regex_list : List[Pattern] = []
        with open(model_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self._regex_list.append({"label":row["LABEL"], "reg":row["EXP"], "rank":int(row["RANK"])})

    def _get_sensitive_spans(self, text : str) -> List[Span]:
        span_list : List[Span ]= []
        for reg in self._regex_list:
            span_list.extend(
                [{'start': match.span()[0], 'end': match.span()[1], 'label': reg['label'], 'rank' : reg['rank'] } 
                    for match in re.finditer(reg['reg'], text)
                ]) 
        return span_list


