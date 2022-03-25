import argparse

def cleanConll(conllFilePath, outputPath):
    conllInput = []
    with open(conllFilePath, "r") as inputFile:
        conllInput = inputFile.readlines()
    # tags = list(map(detect_name, conllInput))[]
    with open(outputPath, "w") as outputFile:
        for line in conllInput:
            if line == "\n":
                outputFile.write(line)
            else:
                split = line.split("\t")
                
                prev = split[0]
                tag = split[-1]
                outputFile.write(f"{prev}\t{tag}")

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

    cleanConll(inputFilePath, outputFilePath)

if __name__ == "__main__":
    main()