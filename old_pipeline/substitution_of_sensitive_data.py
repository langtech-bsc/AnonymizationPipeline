import string
import random
import json
import argparse

lowers = string.ascii_lowercase
uppers = string.ascii_uppercase
numbers = "0123456789"




def substituteCharacters(span, text):
    beginning = span[0]
    end = span[1]
    newtext = []
    for char in text[beginning:end]:
        if char.isnumeric():
            newtext.append(random.choice(numbers))
        elif char.isalpha():
            if char.isupper():
                newtext.append(random.choice(uppers))
            else:
                newtext.append(random.choice(lowers))
        else:
            newtext.append(char)
    return text[:beginning] + ''.join(newtext) + text[end:]


def anonymizeSpans(spansPath, anonymSpans):
    with open(spansPath, 'r') as spansFile:
        newJsons = []
        for line in spansFile.readlines():
            j = json.loads(line)
            text = j['data']
            for span in j['label']:
                text = substituteCharacters(span,text)
            j['data'] = text
            j['text'] = j.pop('data')
            newJsons.append(json.dumps(j))
    with open(anonymSpans, 'w') as anonymFile:
        anonymFile.writelines([line + '\n' for line in newJsons])

def changeDataLabelForText(spansPath):
    with open(spansPath, 'r') as spansFile:
        newJsons = []
        for line in spansFile.readlines():
            j = json.loads(line)
            j['text'] = j.pop('data')
            newJsons.append(json.dumps(j))
    with open(spansPath, 'w') as spansFile:
        spansFile.writelines([line + '\n' for line in newJsons])
        
    
def main():
    """ Script to process commandline arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, \
        help="File containing jsonl file with the spans to anonymize")
    parser.add_argument("-o", "--output_folder", type=str, \
        help="Folder in which the resulting anonymized file wil be saved")
    #TODO: Make the text and labels fields arguments of the script (sometimes the JsonL might have different names for the fields)

    args = parser.parse_args()
    
    inputFilePath = args.file
    outputFolder = args.output_folder 

    if outputFolder[-1] == "/" :
        outputFolder = outputFolder[:-1]

    anonymizeSpans(inputFilePath, outputFolder+"/anon.jsonl")
    changeDataLabelForText(inputFilePath)

if __name__ == "__main__":
    main()


# anonymizeSpans("../../doccano_test/admin.jsonl", "./anon.jsonl")
# changeDataLabelForText("../../doccano_test/admin.jsonl")

