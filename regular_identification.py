# Thigs that need to be done still
#   - Get regex for other sensitive data 
#       - Credit cards
#       - CIP Code
#   - Change the license plate regex so that it doesn't coincide with phone numbers
#   - Perform the name identification with ROBERTa-base-concat

from functools import reduce
from os import error, pardir
from unidecode import unidecode
import re
import argparse

# Regexs used
REG_EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
REG_TELEPHONE = r"(\+|00)?(34)?((/[^\S\r\n]/|.)?[0-9]{2,3}\.?){3,4}"
REG_BANK = r"([A-Z]{2}[0-9]{2} ?)?([0-9]{4} ?){2}[0-9]{2} ?[0-9]{10}"
REG_BANK2 = r"[A-Z]{4} ?([A-Z]{2} ?){2}[0-9]{3}"
REG_ID = r"[0-9]{8}[A-Z]{1}|[A-Z]{1}[0-9]{8}|[A-Z]{3}[0-9]{6}"
#TODO: Fix the license plate regex because it picks the phone numbers and short numbers as well.
REG_LICENSE_PLATE = r"[A-Z]{0,3}[ -]?[0-9]{4,6}[ -]?[A-Z]{0,3}"
#TODO: add the regex for the credit cards
#TODO: add the regex for the CIP code


REGEX_LIST = [
    {'label': "EMAIL", 'reg':REG_EMAIL}
    , {'label': "FINANCIAL", 'reg':REG_BANK}
    , {'label': "FINANCIAL", 'reg':REG_BANK2}
    , {'label': "TELEPHONE", 'reg':REG_TELEPHONE}
    , {'label': "ID", 'reg':REG_ID}
    # , {'label': "LICENSE_PLATE", 'reg':REG_LICENSE_PLATE}
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



def plainToBrat(filePath, outputPath):
    """ Reads the input file in plain text and produces BRAT output (only tags) of the entities in the top of the file using regex
    """
    tags = []
    with open(filePath, "r") as liaFile:
        text = liaFile.read()
    for reg in REGEX_LIST:
        for match in re.finditer(reg['reg'], text):
            tags.append({'tag': reg['label'], "span": match.span(), "text": match.group()})
    sorted_tags = sorted(tags, key=lambda dic: dic['span']) 
    with open(outputPath, "w") as outputFile:
        for index, tag in enumerate(sorted_tags):
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

# text = ""
# for reg in REGEX_LIST:
#     for match in re.finditer(reg['reg'], text):
#         print(match)
#         print(reg['label'])
        
