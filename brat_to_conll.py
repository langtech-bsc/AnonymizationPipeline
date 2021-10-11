# -*- coding: utf-8 -*-
import codecs
import glob
import json
import os
import re
import argparse

from pycorenlp import StanfordCoreNLP
import spacy
from spacy.language import Language

import utils_nlp


def get_start_and_end_offset_of_token_from_spacy(token):
    start = token.idx
    end = start + len(token)
    return start, end


def get_sentences_and_tokens_from_spacy(text, spacy_nlp):
    document = spacy_nlp(text)
    # sentences
    sentences = []
    for span in document.sents:
        sentence = [document[i] for i in range(span.start, span.end)]
        sentence_tokens = []
        for token in sentence:
            token_dict = {}
            token_dict['start'], token_dict['end'] = get_start_and_end_offset_of_token_from_spacy(token)
            token_dict['text'] = text[token_dict['start']:token_dict['end']]
            if token_dict['text'].strip() in ['\n', '\t', ' ', '']:
                continue
            # Make sure that the token text does not contain any space
            if len(token_dict['text'].split(' ')) != 1:
                print(
                    "WARNING: the text of the token contains space character, replaced with hyphen\n\t{0}\n\t{1}".format(
                        token_dict['text'],
                        token_dict['text'].replace(' ', '-')))
                token_dict['text'] = token_dict['text'].replace(' ', '-')
            sentence_tokens.append(token_dict)
        sentences.append(sentence_tokens)
    return sentences


def get_stanford_annotations(text, core_nlp, port=9000, annotators='tokenize,ssplit,pos,lemma'):
    output = core_nlp.annotate(text, properties={
        "timeout": "10000",
        "ssplit.newlineIsSentenceBreak": "two",
        'annotators': annotators,
        'outputFormat': 'json'
    })
    if type(output) is str:
        output = json.loads(output, strict=False)
    return output


def get_sentences_and_tokens_from_stanford(text, core_nlp):
    stanford_output = get_stanford_annotations(text, core_nlp)
    sentences = []
    for sentence in stanford_output['sentences']:
        tokens = []
        for token in sentence['tokens']:
            token['start'] = int(token['characterOffsetBegin'])
            token['end'] = int(token['characterOffsetEnd'])
            token['text'] = text[token['start']:token['end']]
            if token['text'].strip() in ['\n', '\t', ' ', '']:
                continue
            # Make sure that the token text does not contain any space
            if len(token['text'].split(' ')) != 1:
                print(
                    "WARNING: the text of the token contains space character, replaced with hyphen\n\t{0}\n\t{1}".format(
                        token['text'],
                        token['text'].replace(' ', '-')))
                token['text'] = token['text'].replace(' ', '-')
            tokens.append(token)
        sentences.append(tokens)
    return sentences


def get_entities_from_brat(text_filepath, annotation_filepath, verbose=False):
    # load text
    with codecs.open(text_filepath, 'r', 'UTF-8') as f:
        text = f.read()
    if verbose: print("\ntext:\n{0}\n".format(text))

    # parse annotation file
    entities = []
    with codecs.open(annotation_filepath, 'r', 'UTF-8') as f:
        for line in f.read().splitlines():
            anno = line.split()
            id_anno = anno[0]
            # parse entity
            if id_anno[0] == 'T':
                multiline_indexs = [2] # put an initial 2
                multiline_indexs += [i for i, content in enumerate(anno) if re.match("[0-9]+;[0-9]+", content) is not None]
                annotation_text = ' '.join(anno[multiline_indexs[-1]+2:])
                annotation_start = int(anno[2])
                text_index = multiline_indexs[-1]+2

                # first spans
                for i in multiline_indexs:
                    entity = {}
                    entity['id'] = id_anno
                    entity['type'] = anno[1]
                    if i == 2:
                        entity['start'] = annotation_start
                    else:
                        entity['start'] = int(anno[i].split(';')[1])
                    entity['end'] = int(anno[i+1].split(';')[0]) # works for both with ; and without
#                     entity['text'] = annotation_text[entity['start'] - annotation_start:entity['end'] - annotation_start]
                    accumulated_text = ""
                    while entity['end'] - entity['start'] > len(accumulated_text) and text_index < len(anno):
                        if accumulated_text != "": accumulated_text += ' '
                        accumulated_text += anno[text_index]
                        text_index += 1
                    entity['text'] = accumulated_text

                    if verbose:
                        print("entity: {0}".format(entity))

                    # Check compatibility between brat text and anootation
                    if utils_nlp.replace_unicode_whitespaces_with_ascii_whitespace(text[entity['start']:entity['end']]) != \
                            utils_nlp.replace_unicode_whitespaces_with_ascii_whitespace(entity['text']):
                                print(f"Warning: brat text and annotation do not match in '{os.path.basename(annotation_filepath)}'.")
                                print("\ttext: {0}".format(text[entity['start']:entity['end']]))
                                print(f"\tanno: {entity['text']} ({entity['start']}-{entity['end']})")
                    # add to entitys data
                    entities.append(entity)
                
    if verbose: print("\n\n")
    return text, entities


def check_brat_annotation_and_text_compatibility(brat_folder):
    '''
    Check if brat annotation and text files are compatible.
    '''
    dataset_type = os.path.basename(brat_folder)
    print("Checking the validity of BRAT-formatted {0} set... ".format(dataset_type), end='')
    text_filepaths = sorted(glob.glob(os.path.join(brat_folder, '*.txt')))
    for text_filepath in text_filepaths:
        base_filename = os.path.splitext(os.path.basename(text_filepath))[0]
        annotation_filepath = os.path.join(os.path.dirname(text_filepath), base_filename + '.ann')
        # check if annotation file exists
        if not os.path.exists(annotation_filepath):
            raise IOError("Annotation file does not exist: {0}".format(annotation_filepath))
        text, entities = get_entities_from_brat(text_filepath, annotation_filepath)
    print("Done.")


def brat_to_conll(input_folder, output_filepath, tokenizer, language, colon_split, new_line_split):
    '''
    Assumes '.txt' and '.ann' files are in the input_folder.
    Checks for the compatibility between .txt and .ann at the same time.
    '''
    if tokenizer == 'spacy':
        spacy_nlp = spacy.load(language)
        if(colon_split):
            infixes = spacy_nlp.Defaults.suffixes + [r","]
            infix_regex = spacy.util.compile_infix_regex(infixes)
            spacy_nlp.tokenizer.infix_finditer = infix_regex.finditer
        if (new_line_split):
            def is_nl_token(t):
                # if a token consists of all space, and has at least one newline char, we segment as a sentence.
                if t.is_space and '\n' in t.text:
                    return True
                else:
                    return False

            @Language.component("set_sent_starts")
            def set_sent_starts( doc):
                if is_nl_token(doc[0]):
                    doc[0].is_sent_start = True
                else:
                    doc[0].is_sent_start = False
                if len(doc) == 1:
                    return doc

                for t in doc[1:]:
                    if is_nl_token(doc[t.i - 1]) and not is_nl_token(t):
                        t.is_sent_start = True
                    else:
                        t.is_sent_start = False

                return doc
            spacy_nlp.add_pipe("set_sent_starts", before='parser')

    elif tokenizer == 'stanford':
        core_nlp = StanfordCoreNLP('http://localhost:{0}'.format(9000))
    else:
        raise ValueError("tokenizer should be either 'spacy' or 'stanford'.")
    verbose = False
    dataset_type = os.path.basename(input_folder)
    print("Formatting {0} set from BRAT to CONLL... ".format(dataset_type), end='')
    text_filepaths = sorted(glob.glob(os.path.join(input_folder, '*.txt')))
    output_file = codecs.open(output_filepath, 'w', 'utf-8')
    for text_filepath in text_filepaths:
        base_filename = os.path.splitext(os.path.basename(text_filepath))[0]
        annotation_filepath = os.path.join(os.path.dirname(text_filepath), base_filename + '.ann')
        # create annotation file if it does not exist
        if not os.path.exists(annotation_filepath):
            codecs.open(annotation_filepath, 'w', 'UTF-8').close()

        text, entities = get_entities_from_brat(text_filepath, annotation_filepath)
        entities = sorted(entities, key=lambda entity: entity["start"])

        if tokenizer == 'spacy':
            sentences = get_sentences_and_tokens_from_spacy(text, spacy_nlp)
        elif tokenizer == 'stanford':
            sentences = get_sentences_and_tokens_from_stanford(text, core_nlp)

        for sentence in sentences:
            inside = False
            previous_token_label = 'O'
            for token in sentence:
                token['label'] = 'O'
                for entity in entities:
                    if entity['start'] <= token['start'] < entity['end'] or \
                            entity['start'] < token['end'] <= entity['end'] or \
                            token['start'] < entity['start'] < entity['end'] < token['end']:

                        token['label'] = entity['type'].replace('-',
                                                                '_')  # Because the ANN doesn't support tag with '-' in it

                        break
                    elif token['end'] < entity['start']:
                        break

                if len(entities) == 0:
                    entity = {'end': 0}
                if token['label'] == 'O':
                    gold_label = 'O'
                    inside = False
                elif inside and token['label'] == previous_token_label:
                    gold_label = 'I-{0}'.format(token['label'])
                else:
                    inside = True
                    gold_label = 'B-{0}'.format(token['label'])
                if token['end'] == entity['end']:
                    inside = False
                previous_token_label = token['label']
                if verbose: print(
                    f"{token['text']}\t{base_filename}\t{token['start']}_{token['end']}\t{gold_label}\n")
                output_file.write(
                    f"{token['text']}\t{base_filename}\t{token['start']}_{token['end']}\t{gold_label}\n")
            if verbose: print('\n')
            output_file.write('\n')

    output_file.close()
    print('Done.')
    if tokenizer == 'spacy':
        del spacy_nlp
    elif tokenizer == 'stanford':
        del core_nlp


def main():
    """ Script to process commandline arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_directory", type=str, \
            help="name of the directory containing the brat files.")
    parser.add_argument("-p", "--path", type=str, \
            help="path to the input directory that contains all the brat files to be converted to conll. If the input directory is 'r', then it will search recursively for all the subdirectories to find the folders named as the --input_directory. Default: 'r'",\
            default='r')
    parser.add_argument("-o", "--output_file", type=str, \
            help="name of the output conll file. Default: output_conll",
            default="output_conll")
    parser.add_argument("-t", "--tokenizer", type=str, \
            help="tokenizer to be used. Choices=[spacy, stanford]. Default=spacy",
            choices=["spacy", "stanford"],
            default="spacy")
    parser.add_argument("-l", "--language", type=str, \
            help="language to be used. Default: es_core_news_sm",\
            default="es_core_news_sm")
    parser.add_argument("-cp", "--colon_split", type=bool, \
            help="determines if the split by colon is performed always or if the split by colon is determined by the tokenizer.", \
            default=True)
    parser.add_argument("-nls", "--new_line_split", type=bool, \
            help="determines if the sentence boundary should only be new lines.", \
            default=True)
    
    args = parser.parse_args()

    path        = args.path
    input_dir   = args.input_directory
    output_dir  = args.output_file
    tokenizer   = args.tokenizer
    language    = args.language
    colon_split = args.colon_split
    new_line_split = args.new_line_split

    if path == 'r':
        for root, subdirs, _ in os.walk('.'):
            if os.path.isdir(os.path.join(root, input_dir)):
                brat_to_conll(os.path.join(root, input_dir),
                              os.path.join(root, output_dir),
                              tokenizer,
                              language, colon_split, new_line_split)
    else:
        brat_to_conll(os.path.join(path, input_dir),
                      os.path.join(path, output_dir),
                      tokenizer,
                      language, colon_split, new_line_split)


if __name__ == "__main__":
    main()
#     for root, subdirs, _ in os.walk('.'):
#         if (os.path.isdir(os.path.join(root, input_dir))):
#             brat_to_conll(os.path.join(root, input_dir), 
#                           os.path.join(root, output_dir),
#                           "spacy", 
#                           "es_core_news_sm")
