from __future__ import annotations

from typing import List, TypedDict
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

    def identify_sensitive(self, registry : Registry) -> None:
        for reg in self._regex_list:
            for match in re.finditer(reg['reg'], registry.text):
                registry.add_span({'start': match.span()[0], 'end': match.span()[1], 'label': reg['label'], 'rank' : reg['rank'] })


