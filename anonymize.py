from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
import faker
import babel.dates

# This file will contain the scripts for anonymizing spans

import string
import random
from typing import Callable, Dict, List, Tuple


from meta import Span


lowers: str = string.ascii_lowercase
uppers: str = string.ascii_uppercase
numbers: str = "0123456789"


def anonymizeSpans(anonymizer : Anonymizer, spans: List[Span], text: str) -> Tuple[List[Span], str]:
    new_spans = []
    offset = 0
    for span in spans:
        span["start"]+= offset
        span["end"]+= offset
        new_span, new_text = anonymizer.anonymize(span, text)
        text = new_text
        offset += new_span["end"] - span["end"]
        new_spans.append(new_span)
    return (new_spans, text)


def _random_replace(text : str) -> str:
    new_text: List[str] = []
    for char in text:
        if char.isnumeric():
            new_text.append(random.choice(numbers))
        elif char.isalpha():
            if char.isupper():
                new_text.append(random.choice(uppers))
            else:
                new_text.append(random.choice(lowers))
        else:
            new_text.append(char)
    return "".join(new_text)

class Anonymizer(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def anonymize(self, span: Span, text: str) -> Tuple[Span, str]:
        pass


class RandomAnonym(Anonymizer):

    def __init__(self) -> None:
        super().__init__()

    def anonymize(self, span: Span, text: str) -> Tuple[Span, str]:
        start: int = span['start']
        end: int = span['end']
        new_text: List[str] = []
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
        return (span.copy(), text[:start] + "".join(new_text) + text[end:])

class LabelAnonym(Anonymizer):

    def __init__(self) -> None:
        super().__init__()

    def anonymize(self, span: Span, text: str) -> Tuple[Span, str]:
        start: int = span['start']
        end: int = span['end']
        label = span["label"]
        new_text: str = f"<{label}>"
        new_span = span.copy()
        new_span["end"] = new_span["start"] + len(new_text)
        return (new_span, text[:start] + new_text + text[end:])


class AllAnonym(Anonymizer):
    def __init__(self) -> None:
        super().__init__()
        # TODO: Put all files in a gazeteer dictionary
        # Get name files
        # TODO: Change for DataFrame
        names_path = "data/names/names_no_rep.txt"
        surnames_path = "data/names/surnames.txt"
        self._name_list = []
        self._surname_list = []
        with open(names_path, "r") as f:
            for line in f:
                self._name_list.append(line.strip())
        with open(surnames_path, "r") as f:
            for line in f:
                self._surname_list.append(line.strip())

        # Get location files
        nomenclator_path = "data/nomenclator.csv"
        barrios_path = "data/distritos_barrios.txt"
        self._nomenclator = pd.read_csv(nomenclator_path)
        with open(barrios_path, "r") as f:
            self._barrios = [x.strip() for x in f.read().splitlines()]

        # Select specific locations
        self.streets = self._nomenclator.loc[self._nomenclator['TIPUS_VIA'].isin(
            ["carrer", "via", "carreró", "avinguda", "passeig"])]
        self.parks = self._nomenclator.loc[self._nomenclator["TIPUS_VIA"].isin(
            ["jardí", "placeta", "plaça", "jardins", "parc"])]

        self.replace_dict: Dict[str, Callable[[str], str]] = {
            "PER": self._replacePER,
            "LOC": self._replaceLOC,
            "DATE": self._replaceDATE,
            "ZIP": self._replaceZIP,
            "ID": self._replaceID,
            "FINANCIAL": self._replaceFINANCIAL,
            "VEHICLE": self._replaceVEHICLE,
            "CARD": self._replaceCARD,
            "OTHER": self._replaceDefault,
            "SENSITIVE": self._replaceDelete,
        }

    def anonymize(self, span: Span, text: str) -> Tuple[Span, str]:
        old_text : str = text[span["start"]:span["end"]]
        new_text = self._replaceDefault(old_text) if span["label"] not in self.replace_dict else self.replace_dict[span["label"]](old_text)
        new_span = span.copy()
        new_span["end"] = new_span["start"] + len(new_text)
        return (new_span, text[:span["start"]] + new_text + text[span["end"]:])

    def _replacePER(self, text: str) -> str:
        subwords = text.split()
        if len(subwords) == 1:  # Single name
            new_text = self.generateName(text)
        else:  # Full name
            name = self.generateName(subwords[0])
            surname = self.generateSurname(subwords[1])
            new_text = f"{name} {surname}"
        return  new_text

    def _fix_particule(self, selection) -> str:
        if type(selection['PARTICULES']) == str: # Check because some entries in nomenclator don't have particle
            if "'" in selection["PARTICULES"]:
                return f"{selection['TIPUS_VIA']} {selection['PARTICULES']}{selection['NOM']}"
            else: 
                return f"{selection['TIPUS_VIA']} {selection['PARTICULES']} {selection['NOM']}"
        else: 
            return f"{selection['TIPUS_VIA']} {selection['NOM']}"

    def _replaceLOC(self, text: str) -> str:
        # TODO: Detect if it is a city (Barcelona, L'Hospitalet de Lobregat, Sabadell, etc) to replace it with a city names
        lower = text.lower()
        intersections = [" amb ", " i ", "cantonada", " con ", " y "]
        
        if any(char.isdigit() for char in lower):  # Full street address
            selection = self.streets.sample(1).iloc[0]
            # With descriptor
            if any(x in lower for x in ["carrer", "calle", "vía", "via", "carrero", "carreró"]):
                address = f"{self._fix_particule(selection)} {random.randint(1,100)}"
            else:
                address = f"{selection['NOM']} {random.randint(1,100)}"
        else:
            intersecting_selection = [inter for inter in intersections if inter in lower]
            if len(intersecting_selection) > 0:  # intersection
                two_street_slection = self.streets.sample(2)
                street1 = two_street_slection.iloc[0]
                street2 = two_street_slection.iloc[1]
                address1 = f"{self._fix_particule(street1)}"
                address2 = f"{self._fix_particule(street2)}"
                address = address1 + \
                    f" {random.choice(intersecting_selection)} " + address2
            elif any(x in lower for x in ["districte", "district", "distrito", "barrio", "barri", "zona"]): # Barrio
                address = random.choice(self._barrios)            
            elif any(x in lower for x in ["park", "parque", "jardín", "parc", "plaça"]): # Parque o jardín
                selection = self.parks.sample(1).iloc[0]
                address = f"{self._fix_particule(selection)}"
            else:  # Single street
                selection = self.streets.sample(1).iloc[0]
                address = f"{self._fix_particule(selection)}"
            
        if text.isupper():
            return address.upper()
        elif text.islower():
            return address.lower()
        else:
            return address

    def _replaceTELEPHONE(self, text: str) -> str:
        return text[:1] + self._replaceDefault(text[1:])

    def _replaceZIP(self, text: str) -> str:
        if text[:2].isnumeric(): # Local zip, we want to keep the first 2 digits
            return text[:2] + self._replaceDefault(text[2:])
        else:
            return self._replaceDefault(text)

    def _replaceID(self, text: str) -> str:
        return self._replaceDefault(text)

    def _replaceDATE(self, text: str) -> str:
        fake = faker.Faker()
        date = fake.date_time_between(start_date="-2y", end_date="now")
        if not any(map(lambda c: c.isalpha(), text)): # contracted numerical date format
            return date.strftime("%d/%m/%Y")
        elif any(map(lambda word: word in text.lower(), ["'", "gener", "febrer ", "març", "maig", "juny", "juliol", "agost ", "setembre", "novembre", "desembre"])) : # catalan date
            return babel.dates.format_date(date, "long", locale="ca")
        else: 
            return babel.dates.format_date(date, "long", locale="es")

    def _replaceFINANCIAL(self, text: str) -> str:
        if text[0].isalpha(): # BANK identifier
            starting = text[:2]
            remaining = text[2:]
            replacement = _random_replace(remaining)
            return starting + replacement
        else: 
            return self._replaceDefault(text)

    def _replaceCARD(self, text: str) -> str:
        return self._replaceDefault(text)

    def _replaceVEHICLE(self, text: str) -> str:
        return self._replaceDefault(text)

    def _replaceDefault(self, text: str) -> str:
        return _random_replace(text)

    def _replaceDelete(self, text: str) -> str:
        return ""

    #TODO: Move all this logic to a subclass maybe?
    #-------------------------------------------------------
    @staticmethod
    def _format_string(text: str, replacement: str) -> str:
        if text[0].isupper():
            if len(text) > 1 and text[1].isupper():  # All Caps
                return replacement.upper()
            else:  # Capitalized
                return replacement.capitalize()
        else:  # All lower
            return replacement

    def generateName(self, text: str) -> str:
        name = random.choice(self._name_list)
        return self._format_string(text, name)

    def generateSurname(self, text: str) -> str:
        surname = random.choice(self._surname_list)
        return self._format_string(text, surname)
    #-------------------------------------------------------

