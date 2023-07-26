from typing import List
import anonymize
import ingestors
from sensitive_identification.name_identifiers import RoBERTaNameIdentifier, SpacyIdentifier
from sensitive_identification.regex_identification import RegexIdentifier
import configargparse
from tqdm import tqdm
from copy import deepcopy

from sensitive_identification.sensitive_identifier import SensitiveIdentifier
from truecaser.TrueCaser import TrueCaser

tc = TrueCaser('truecaser/spanish.dist')

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
    parser.add_argument("-m", "--models", type=str, nargs="*", \
        help="List of paths to the NER models", default=["es_anonimization_core_lg", "xx_ent_wiki_sm"])
    parser.add_argument("-t", "--type_of_models", nargs="*", choices=["spacy", "huggingface"], default=["spacy", "spacy"], \
        help="List of the type of NER models (must coincide with list of paths length)")
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
    model_paths : List[str] = args.models
    model_types : List[str] = args.type_of_models
    input_format : str = args.format
    anonym_method : str = args.anonym_method
    labels : str = args.labels
    regex_definitions : str = args.regexes

    assert len(model_paths) == len(model_types), "List of model paths and list of types must be of same length"
    label_list = None
    if labels:
        label_list = get_labels(labels)
    ner_models : List[SensitiveIdentifier] = []
    print("Loading models")
    for model_path, model_type in zip(model_paths, model_types):
        if model_type == "spacy":
            ner_models.append(SpacyIdentifier(model_path, label_list))
        else:
            ner_models.append(RoBERTaNameIdentifier(model_path, label_list))
    print("Finished loading model")

    if input_format == "plain":
        ingestor = ingestors.PlainTextingestor(input_path)
    elif input_format == "jsonl":
        ingestor = ingestors.Prodigyingestor(input_path)
    else:
        ingestor = ingestors.Doccanoingestor(input_path)


    regex_identifier = RegexIdentifier(regex_definitions, label_list)
    
    for reg in tqdm(ingestor.registries, "Sensitive data identification"):
        original_reg = deepcopy(reg)
        reg.text = tc.get_true_case(reg.text)
        regex_identifier.identify_sensitive(reg)
        for ner_model in ner_models:
            ner_model.identify_sensitive(reg)
        reg.text = original_reg.text

    if anonym_method != "none":
        print("Instantiating anonymizer")
        if anonym_method == "label":
            anonymizer = anonymize.LabelAnonym()
        elif anonym_method == "random":
            anonymizer = anonymize.RandomAnonym()
        else: 
            anonymizer = anonymize.AllAnonym()
        ingestor.anonymize_registries(anonymizer)

    ingestor.save(output_path)


if __name__ == "__main__":
    main()
