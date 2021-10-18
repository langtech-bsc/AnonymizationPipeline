# Thigs that need to be done still
#   - Perform the name identification with ROBERTa-base-concat

from functools import reduce
from os import error, pardir
from unidecode import unidecode
import re
import argparse
from roberta_name_loc_identification import identifyNames

# Regexs used
REG_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# Change phone regex so that it picks phones from outside Spain (i.e. make the +34 generic)
#OLD_REG_TELEPHONE = r"(\+|00)?(34)?((/[^\S\r\n]/|.)?[0-9]{2,3}\.?){3,4}"
REG_TELEPHONE = r"\b(\+|00)?(34)?(( |\.)?[0-9]{2,3}\.?){3,4}\b"
REG_BANK = r"([A-Z]{2}[0-9]{2} ?)?([0-9]{4} ?){2}[0-9]{2} ?[0-9]{10}"
REG_BANK2 = r"[A-Z]{4} ?([A-Z]{2} ?){2}[0-9]{3}"
#OLD_REG_ID = r"[0-9]{8}[a-zA-Z]{1}|[a-zA-Z]{1}[0-9]{8}|[a-zA-Z]{3}[0-9]{6}"
REG_ID = r"[0-9]{8}[a-zA-Z]{1}|[a-zA-Z]{1}[0-9]{8}|[a-zA-Z]{3}[0-9]{6}|[a-zA-Z][0-9]{7,8}[a-zA-Z]|[0-9]{2} ?[0-9]{8}"
#OLD_REG_LICENSE_PLATE: r"[A-Z]{0,3}[ -]?[0-9]{4,6}[ -]?[A-Z]{0,3}"
REG_LICENSE_PLATE = r"[a-zA-Z] ?-? ?[0-9]{4} ?-? ?[a-zA-Z]{3}"
REG_CARD = r"\b(?:\d[ -]*?){13,16}\b"
REG_ZIP = r"\b[0-9]{5}\b"


REGEX_LIST = [
    {'label': "EMAIL", 'reg':REG_EMAIL}
    , {'label': "FINANCIAL", 'reg':REG_BANK}
    , {'label': "FINANCIAL", 'reg':REG_BANK2}
    , {'label': "TELEPHONE", 'reg':REG_TELEPHONE}
    , {'label': "ID", 'reg':REG_ID}
    , {'label': "LICENSE_PLATE", 'reg':REG_LICENSE_PLATE}
    , {'label': "CARD", 'reg': REG_CARD}
    , {'label': "ZIP", 'reg':REG_ZIP}
    ]

def tokenRegLabel(line):
    for reg in REGEX_LIST:
        if re.match(reg['reg'], str(line[0])):
            return reg['label']
    return 'O'

def susbstitudePlainText(line):
    for reg in REGEX_LIST:
        line = re.sub(reg['reg'], f" [{reg['label']}]", line)
    return line

def mergeSpans(span1, span2, original_text):
    combined_span = (min(span1['span'][0], span2['span'][0]), max(span1['span'][1], span2['span'][1]))
    combined_text = text[combined_span[0]:combined_span[1]]
    combined = {'tag':span1['tag'], 'span':combined_span, 'text':combined_text}
    return combined

def resolveOverlapping(sorted_tags, original_text):
    index = 0
    while index < len(sorted_tags) - 1:
        current_span = sorted_tags[index]
        next_span = sorted_tags[index+1]
        if not areOverlapping(current_span, next_span):
            index += 1
        else:
            #TODO: Review if I should delete this case (since it will never happen) because spans are sorted by start and then by end
            if next_span['span'][1] < current_span['span'][1]: # The next_span is inside the current_span
                sorted_tags.pop(index + 1)
            elif current_span['span'][0] == next_span['span'][0] and current_span['span'][1] < next_span['span'][1]: # The current_span is inside the next_span
                sorted_tags.pop(index)
            else: 
                if current_span['tag'] == next_span['tag']: # The 2 spans are of the same tag and are overlapping, will merge
                    combined_span = mergeSpans(current_span, next_span, original_text)
                    sorted_tags[index] = combined_span
                    sorted_tags.pop(index + 1)
                else: # 2 different spans are intersecting will choose the longest one.
                    length_current_span = current_span['span'][1] - current_span['span'][0]
                    length_next_span = next_span['span'][1] - next_span['span'][0]
                    if length_current_span < length_next_span:
                        sorted_tags.pop(index)
                    else:
                        sorted_tags.pop(index + 1)
    return sorted_tags

def areOverlapping(span1, span2):
    start_span1 = span1['span'][0]
    start_span2 = span2['span'][0]
    end_span1 = span1['span'][1]
    end_span2 = span2['span'][1]
    return (start_span1 <= start_span2 and start_span2 < end_span1) or (start_span2 <= start_span1 and start_span1 < end_span2)


def plainToBrat(filePath, outputPath):
    """ Reads the input file in plain text and produces BRAT output (only tags) of the entities in the top of the file using regex
    """
    tags = []
    with open(filePath, "r") as liaFile:
        text = liaFile.read()
    for reg in REGEX_LIST:
        for match in re.finditer(reg['reg'], text):
            tags.append({'tag': reg['label'], "span": match.span(), "text": match.group()})
    name_tags = identifyNames(text)
    tags = tags + name_tags
    sorted_tags = sorted(tags, key=lambda dic: dic['span']) 
    # The overlapping resolution will be determined by the following rules:
    # - A span that is inside the scope of another will be suppressed
    # - If 2 spans are overlapping and have the same tag, they will be merged
    # - If 2 spans are overlapping and they don't have the same tag, the longest one will be maintained and the other will be suppressed
    non_overlapping_tags = resolveOverlapping(sorted_tags, text)
    with open(outputPath, "w") as outputFile:
        for index, tag in enumerate(non_overlapping_tags):
            outputFile.write(f"T{index}\t{tag['tag']} {tag['span'][0]} {tag['span'][1]}\t{tag['text']}\n")


def main():
    """ Script to process commandline arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, \
        help="File containing the original text with a context per line.")
    parser.add_argument("-o", "--output", type=str, \
        help="File that will contain the resulting annotation in brat format.", default="output/tmp/regular_identification.ann")

    args = parser.parse_args()
    
    inputFilePath = args.file
    outputFilePath = args.output

    plainToBrat(filePath=inputFilePath, outputPath=outputFilePath)

if __name__ == "__main__":
    main()


# Testing
# plainToBrat("example_text/example.txt", "example_text/test.txt")

# text = "Hola Marta, me esta funcionando mal el telefono. Mi numero es 617761843 y me encuentro en Carrer del Cent 65, 08014, Barcelona, Espana. Deberia llamar o quieres que te pase mis datos bancarios? juanCa_selsen@outlook.org es mi corre y luego ES21 2100 2527 33 1234567890 es la cuenta. Buenos día a todos. Hoy vamos a estar trabajando en un proyecto de Integración entre todos. Nos reuniremos en el café Batac en Calle de Aragón 34, a las 17:35. Marc y Joan no se si van a estar leyendo esto o no, pero les dejo un mensaje y sus DNIs aquí por si las dudas. Y3364793V y A7484842Z."

#tags = []
#for reg in REGEX_LIST:
    #for match in re.finditer(reg['reg'], text):
        #tags.append({'tag': reg['label'], "span": match.span(), "text": match.group()})
#sorted_tags = sorted(tags, key=lambda dic: dic['span']) 
#non_overlapping_tags = resolveOverlapping(sorted_tags, text)
#for match in non_overlapping_tags:
    #print(match)
    #print(match['tag'])

#tags = [{'tag': 'TELEPHONE', 'span': (61, 71), 'text': ' 617761843'}, {'tag': 'TELEPHONE', 'span': (62,76), 'text': '17761843 y me'}]

#print( resolveOverlapping(tags, text))
