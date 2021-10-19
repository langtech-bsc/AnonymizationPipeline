import argparse
from regular_identification import identifyRegular
from roberta_name_loc_identification import ROBERTaNameIdentifier

def mergeSpans(span1, span2, original_text):
    combined_span = (min(span1['span'][0], span2['span'][0]), max(span1['span'][1], span2['span'][1]))
    combined_text = original_text[combined_span[0]:combined_span[1]]
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

def offsetAnnotations(tags, position_offset):
    for entity in tags:
        entity.update({'span':(entity['span'][0] + position_offset, entity['span'][1] + position_offset)})
    return tags

def plainToBrat(filePath, outputPath):
    """ Reads the input file in plain text and produces BRAT output (only tags) of the entities in the top of the file using regex
    """
    with open(filePath, "r") as inputFile:
        lines = inputFile.readlines()
        inputFile.seek(0)
        text = inputFile.read()

    position_offset = 0
    tags = identifyRegular(text)
    nameIdentifier = ROBERTaNameIdentifier()
    for index, line in enumerate(lines):
        print(f"Processing Line {index + 1} of {len(lines)}")
        
        name_tags = nameIdentifier.identifyNames(line)
        name_tags = offsetAnnotations(name_tags, position_offset)
        tags += name_tags
        position_offset += len(line)
    
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
        help="File that will contain the resulting annotation in brat format.", default="output/tmp/sensitive_identification.ann")

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