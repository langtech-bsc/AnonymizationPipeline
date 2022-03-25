from __future__ import annotations

# This file will contain the scripts for anonymizing spans

import string
import random
from typing import List

from meta import Span


lowers : str = string.ascii_lowercase
uppers : str = string.ascii_uppercase
numbers : str = "0123456789"



def anonymizeSpans(spans : List[Span], text : str) -> str :
    for span in spans:
        text = anonymize(span, text)
    return text

def anonymize(span : Span, text : str) -> str: 
    start : int = span['start']
    end : int = span['end']
    new_text : List[str] = [] 
    for char in text[start:end]:
        if char.isnumeric():
            new_text.append(random.choice(numbers))
        elif char.isalpha():
            if char.isupper():
                new_text.append(random.choice(uppers))
            else:
                new_text.append(random.choice(lowers))
        else: 
            new_text.append(char)
    return text[:start] + "".join(new_text) + text[end:]

