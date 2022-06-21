from __future__ import annotations
from abc import ABC
import pandas as pd

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

class Anonymizer(ABC):

    def __init__(self) -> None:
        super().__init__()

    def anonymize(self, span : Span, text : str) -> str:
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

class PERAnonymizer(Anonymizer):
    
    def __init__(self) -> None:
        super().__init__()
        names_path = "names/names_no_rep.txt"
        surnames_path = "names/surnames.txt"
        self._name_list = []
        self._surname_list = []
        with open(names_path, "r") as f:
            for line in f:
                self._name_list.append(line.strip())
        with open(surnames_path, "r") as f:
            for line in f:
                self._surname_list.append(line.strip())

    def anonymize(self, span: Span, context: str) -> str:
        text = context[span["start"]:span["end"]]
        subwords = text.split()
        if len(subwords) == 1: # Single name
            new_text = self.generateName(text)
        else: # Full name
            name = self.generateName(subwords[0])
            surname = self.generateSurname(subwords[1])
            new_text = f"{name} {surname}"
        return context[:span["start"]] + new_text + context[span["end"]:]
    
    @staticmethod
    def _format_string(text : str, replacement : str) -> str:
        if text[0].isupper():
            if text[1].isupper(): # All Caps
                return replacement.upper()
            else: # Capitalized
                return replacement.capitalize()
        else: # All lower
            return replacement

    def generateName(self, text : str) -> str:
        name = random.choice(self._name_list)
        return self._format_string(text, name)

    def generateSurname(self, text : str) -> str:
        surname = random.choice(self._surname_list)
        return self._format_string(text, surname)

class LOCAnonymizer(Anonymizer):
    
    def __init__(self) -> None:
        super().__init__()
        nomenclator_path = "nomenclator.csv"
        barrios_path = "distritos_barrios.txt"
        self._nomenclator = pd.read_csv(nomenclator_path)
        with open(barrios_path, "r") as f:
            self._barrios = [x.strip() for x in f.read().splitlines()]



    
    def anonymize(self, span: Span, text: str) -> str:
        # TODO: Take into account upper cases (all upper, single upper after descriptor, all lower)
        # TODO: Make the conjunction word be the same in the output. 
        # TODO: Remove space between PARTICULES and NOM if the PARTICULES ends with '
        # TODO: Detect if it is a city (Barcelona, L'Hospitalet de Lobregat, Sabadell, etc) to replace it with a city names
        lower = text.lower()
        streets = self._nomenclator.loc[self._nomenclator['TIPUS_VIA'].isin(["carrer", "via", "carreró", "avinguda", "passeig"])]
        parks = self._nomenclator.loc[self._nomenclator["TIPUS_VIA"].isin(["jardí", "placeta", "plaça", "jardins", "parc"])]
        if any(char.isdigit() for char in lower): # Full street address
            selection = streets.sample().iloc[0]
            if any(x in lower for x in ["carrer", "calle", "vía", "via", "carrero", "carreró"]): # With descriptor                 
                address = f"{selection['TIPUS_VIA']} {selection['PARTICULES']} {selection['NOM']} {random.randint(1,100)}"
                # return "Carrer de la Torre d'En Damians 12"
            else:
                address = f"{selection['NOM']} {random.randint(1,100)}"
            return address
        else: 
            if " amb " in lower or " i " in lower or " cantonada " in lower: # intersection
                selection = streets.sample(2)
                street1 = selection.iloc[0]
                street2 = selection.iloc[1]
                address1 = f"{street1['TIPUS_VIA']} {street1['PARTICULES']} {street1['NOM']}"
                address2 = f"{street2['TIPUS_VIA']} {street2['PARTICULES']} {street2['NOM']}"
                address = address1 + f" {random.choice(['amb', 'i', 'con', 'y', 'cantonada'])} " + address2
                return address
            elif any(x in lower for x in ["districte", "district", "distrito", "barrio", "barri", "zona"]):
                return random.choice(self._barrios)
            elif any(x in lower for x in ["park", "parque", "jardín", "parc", "plaça"]): # Parque o jardín
                selection = parks.sample().iloc[0]
                address = f"{selection['TIPUS_VIA']} {selection['PARTICULES']} {selection['NOM']}"
                return address
            else: # Single street
                selection = streets.sample().iloc[0]
                address = f"{selection['TIPUS_VIA']} {selection['PARTICULES']} {selection['NOM']}"
                return address

    ## Categories
    ## - Full address (street and number)
    ## - Only street
    ## - 2 Streets (amb, i or cantonada)
    ## - Neighborhood (district, districte, districto, barrio, barri, zona)
    ## - Park (park, parque, jardín, parc, plaça)