from __future__ import annotations

from typing import List, Optional, TypedDict
from meta import Span
from sensitive_identifier import SensitiveIdentifier

from formatters import Registry

# This file will contain the methods for the identification of the regular sensitive data

import re
import sensitive_regex



class Pattern(TypedDict):
    label : str
    reg : str
    rank : int

class RegexIdentifier(SensitiveIdentifier):
    def __init__(self, label_list: Optional[List[str]] = None) -> None:
        super().__init__(label_list)

    #TODO: Move the regex list to reading the whole regex file
    _regex_list : List[Pattern]
    _regex_list = [
        {'label': "EMAIL", 'reg': sensitive_regex.REG_EMAIL, "rank":1}
        , {'label': "FINANCIAL", 'reg': sensitive_regex.REG_BANK, "rank":1}
        , {'label': "FINANCIAL", 'reg': sensitive_regex.REG_BANK2, "rank":1}
        , {'label': "ID", 'reg': sensitive_regex.NEW_REG_ID, "rank":2}
        , {'label': "TELEPHONE", 'reg': sensitive_regex.REG_TELEPHONE, "rank":1}
        , {'label': "VEHICLE", 'reg': sensitive_regex.REG_LICENSE_PLATE, "rank":3}
        , {'label': "FINANCIAL", 'reg': sensitive_regex.REG_BANK + "|" + sensitive_regex.REG_BANK2, "rank":3}
        , {'label': "CARD", 'reg': sensitive_regex.REG_CARD, "rank":1}
        , {'label': "ZIP", 'reg': sensitive_regex.REG_ZIP, "rank":3}
    ]

    def _get_sensitive_spans(self, text : str) -> List[Span]:
        span_list : List[Span ]= []
        for reg in self._regex_list:
            span_list.extend(
                [{'start': match.span()[0], 'end': match.span()[1], 'label': reg['label'], 'rank' : reg['rank'] } 
                    for match in re.finditer(reg['reg'], text)
                ]) 
        return span_list


