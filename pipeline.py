from typing import List
import anonymize
import ingesters
from sensitive_identification.name_identifiers import RoBERTaNameIdentifier, SpacyIdentifier
from sensitive_identification.regex_identification import RegexIdentifier
import configargparse
from tqdm import tqdm

def get_labels(path : str) -> List[str]:
    label_list : List[str] = []
    with open(path, "r") as f:
        for line in f: 
            label_list.append(line.strip())   
    return label_list

def main():
    parser = configargparse.ArgumentParser(formatter_class=configargparse.ArgumentDefaultsHelpFormatter, default_config_files=['./*conf'])
    parser.add('-c', '--config', required=False, is_config_file=True, help='config file path')
    parser.add_argument("-i", "--input", type=str, \
        help="File containing the original text with a context per line.", required=True)
    parser.add_argument("-m", "--model", type=str, \
        help="Path to the model that is going to be used", default="./models/main_model")
    parser.add_argument("-t", "--type_of_model", choices=["spacy", "huggingface"], default="spacy", \
        help="The type of model that is going to be used for the NER recognition phase")
    parser.add_argument("-f", "--format", choices=["plain", "jsonl", "doccano"] , default="plain", \
        help="Format of the input file")
    parser.add_argument("-a", "--anonym_method", choices=["label", "random", "intelligent", "none"], default="none", \
        help="Anonymization technique that is going to be performed over the sensitive identified data")
    parser.add_argument("-o", "--output", type=str, \
        help="File to which the save action is performed", default="output/output.txt")
    parser.add_argument("-l", "--labels", type=str, \
        help="Text file with list of labels to use by the Sensitive Recognition models")
    parser.add_argument("-r", "--regexes", type=str, \
        help="File containing regex for the regex identification in csv format", default="data/regex_definition.csv")

    args = parser.parse_args()
    
    input_path : str = args.input
    output_path : str = args.output
    model_path : str = args.model
    model_type : str = args.type_of_model
    input_format : str = args.format
    anonym_method : str = args.anonym_method
    labels : str = args.labels
    regex_definitions : str = args.regexes

    label_list = None
    if labels:
        label_list = get_labels(labels)

    print("Loading model")
    if model_type == "spacy":
        ner_model = SpacyIdentifier(model_path, label_list)
    else:
        ner_model = RoBERTaNameIdentifier(model_path, label_list)
    print("Finished loading model")
    
    if input_format == "plain":
        ingester = ingesters.PlainTextIngester(input_path)
    elif input_format == "jsonl":
        ingester = ingesters.ProdigyIngester(input_path)
    else:
        ingester = ingesters.DoccanoIngester(input_path)


    regex_identifier = RegexIdentifier(regex_definitions, label_list)
    
    for reg in tqdm(ingester.registries, "Sensitive data identification"):
        regex_identifier.identify_sensitive(reg)
        ner_model.identify_sensitive(reg)

    if anonym_method != "none":
        print("Instantiating anonymizer")
        if anonym_method == "label":
            anonymizer = anonymize.LabelAnonym()
        elif anonym_method == "random":
            anonymizer = anonymize.RandomAnonym()
        else: 
            anonymizer = anonymize.AllAnonym()
        ingester.anonymize_registries(anonymizer)


    ingester.save(output_path)


if __name__ == "__main__":
    main()
