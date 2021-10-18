import re
import unicodedata
import argparse

# female_names_file = "names/female_names_no_rep.txt"
# male_names_file = "names/male_names_no_rep.txt"
all_names_file = "names/names_no_rep.txt"
surnames_file = "names/surnames.txt"


sensitive_words = []
#Old files, don't need to divide between male and female names
# with open(female_names_file, "r") as fmlFile:
#     sensitive_words.extend(fmlFile.readlines())
# with open(male_names_file, "r") as maleFile:
#     sensitive_words.extend(maleFile.readlines())
with open(all_names_file, "r") as namesFile:
    sensitive_words.extend(namesFile.readlines())
with open(surnames_file, "r") as surnFile:
    sensitive_words.extend(surnFile.readlines())
sensitive_words = [w.strip().lower() for w in sensitive_words]


def identify_names(conllFilePath, outputPath, include_spans=False):
    conllInput = []
    with open(conllFilePath, "r") as inputFile:
        conllInput = inputFile.readlines()
    tags = list(map(detect_name, conllInput))
    with open(outputPath, "w") as outputFile:
        for index, line in enumerate(conllInput):
            if line == "\n":
                outputFile.write(line)
            else:
                split = line.split("\t")
                if include_spans:
                    prev = "\t".join(split[:-1])
                else:
                    prev = split[0]
                tag = f"{tags[index]}\n" if split[-1] == "O\n" else split[-1]
                outputFile.write(f"{prev}\t{tag}")

def remove_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def detect_name(line):
    if line == "\n":
        return None
    word = line.split("\t")[0]
    if remove_accents(word.lower()) in sensitive_words: 
        return "B-PER"
    else:
        return "O"

def main():
    """ Script to process commandline arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, \
        help="File containing conll with previous tags.", default="output/text_brat_to_conll.conll")
    parser.add_argument("-o", "--output", type=str, \
        help="File that will contain the resulting conll format", default="output/suggestion.conll")
    
    args = parser.parse_args()
    
    inputFilePath = args.file
    outputFilePath = args.output    

    identify_names(inputFilePath, outputFilePath)

if __name__ == "__main__":
    main()


def names_no_repetition(supress_short_names=True):
    """ Generates the files for female and male names without compund names for regex usage
    """
    files = ["female", "male"]
    word_pattern = re.compile('\w+')
    names = []
    # #Spanish names Gazetteers
    for gender in files:
        name_list = []
        with open(f"names/{gender}_names.txt", "r") as nameFile:
            for sentence in nameFile:
                name_list.extend(re.findall(word_pattern,sentence))
        nameSet = set(name_list)
        if supress_short_names:
            nameSet = [n for n in nameSet if len(n) > 2]
        names += nameSet
    #Catalan names nomenclator
    with open("names/noms_de_persona.csv", "r", encoding="latin-1") as catNamesFile:
        lines = catNamesFile.readlines()[8:]
        name_list = []
        for sentence in lines:
            current_name = [sentence.split(";")[2]]
            if "/" in current_name[0]:
                current_name = current_name[0].split("/")
            for name in current_name:
                if " " in name:
                    name_list.extend(name.split(" "))
                else:
                    name_list.append(name)
        nameSet = set(name_list)
        if supress_short_names:
            nameSet = [n for n in nameSet if len(n) > 2]
        names += nameSet
    names.sort()
    with open(f"names/names_no_rep.txt", "w") as noRepFile:
        for name in names:
            noRepFile.write(f"{name}\n")
            
# names_no_repetition()
