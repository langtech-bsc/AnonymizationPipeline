import math
import pickle
import re
import string

from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer


class TrueCaser(object):
    def __init__(self, dist_file_path):
        with open(dist_file_path, "rb") as distributions_file:
            pickle_dict = pickle.load(distributions_file)
            self.uni_dist = pickle_dict["uni_dist"]
            self.backward_bi_dist = pickle_dict["backward_bi_dist"]
            self.forward_bi_dist = pickle_dict["forward_bi_dist"]
            self.trigram_dist = pickle_dict["trigram_dist"]
            self.word_casing_lookup = pickle_dict["word_casing_lookup"]
        self.detknzr = TreebankWordDetokenizer()

    def get_score(self, prev_token, possible_token, next_token):
        pseudo_count = 5.0

        # Get Unigram Score
        numerator = self.uni_dist[possible_token] + pseudo_count
        denominator = 0
        for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
            denominator += self.uni_dist[alternativeToken] + pseudo_count

        unigram_score = numerator / denominator

        # Get Backward Score
        bigram_backward_score = 1
        if prev_token is not None:
            key = prev_token + "_" + possible_token
            numerator = self.backward_bi_dist[key] + pseudo_count
            denominator = 0
            for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
                key = prev_token + "_" + alternativeToken
                denominator += self.backward_bi_dist[key] + pseudo_count

            bigram_backward_score = numerator / denominator

        # Get Forward Score
        bigram_forward_score = 1
        if next_token is not None:
            next_token = next_token.lower()  # Ensure it is lower case
            key = possible_token + "_" + next_token
            numerator = self.forward_bi_dist[key] + pseudo_count
            denominator = 0
            for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
                key = alternativeToken + "_" + next_token
                denominator += self.forward_bi_dist[key] + pseudo_count

            bigram_forward_score = numerator / denominator

        # Get Trigram Score
        trigram_score = 1
        if prev_token is not None and next_token is not None:
            next_token = next_token.lower()  # Ensure it is lower case
            trigram_key = prev_token + "_" + possible_token + "_" + next_token
            numerator = self.trigram_dist[trigram_key] + pseudo_count
            denominator = 0
            for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
                trigram_key = prev_token + "_" + alternativeToken + "_" + next_token
                denominator += self.trigram_dist[trigram_key] + pseudo_count

            trigram_score = numerator / denominator

        result = (
                math.log(unigram_score)
                + math.log(bigram_backward_score)
                + math.log(bigram_forward_score)
                + math.log(trigram_score)
        )

        return result

    @staticmethod
    def first_token_case(raw):
        return raw.capitalize()

    @staticmethod
    def upper_replacement(match):
        return '. ' + match.group(0)[-1].upper()

    def get_true_case(self, sentence, out_of_vocabulary_token_option="title"):
        # word tokenizer is set for English. Defaulting to whitespace split
        # tokens = word_tokenize(sentence)
        tokens = sentence.split()
        tokens_true_case = self.get_true_case_from_tokens(tokens, out_of_vocabulary_token_option)
        # text = self.detknzr.detokenize(tokens_true_case)
        text = ' '.join(tokens_true_case)
        text = re.sub(r' \. .', self.upper_replacement, text)
        return text

    def get_true_case_from_tokens(self, tokens, out_of_vocabulary_token_option="title"):
        tokens_true_case = []

        if not len(tokens):
            return tokens_true_case

        for token_idx, token in enumerate(tokens):
            if token in string.punctuation or token.isdigit():
                tokens_true_case.append(token)
                continue

            token = token.lower()
            if token not in self.word_casing_lookup:  # Token out of vocabulary
                if out_of_vocabulary_token_option == "title":
                    tokens_true_case.append(token.title())
                elif out_of_vocabulary_token_option == "capitalize":
                    tokens_true_case.append(token.capitalize())
                elif out_of_vocabulary_token_option == "lower":
                    tokens_true_case.append(token.lower())
                else:
                    tokens_true_case.append(token)
                continue

            if len(self.word_casing_lookup[token]) == 1:
                tokens_true_case.append(list(self.word_casing_lookup[token])[0])
                continue

            prev_token = tokens_true_case[token_idx - 1] if token_idx > 0 else None
            next_token = tokens[token_idx + 1] if token_idx < len(tokens) - 1 else None

            best_token = None
            highest_score = float("-inf")

            for possible_token in self.word_casing_lookup[token]:
                score = self.get_score(prev_token, possible_token, next_token)

                if score > highest_score:
                    best_token = possible_token
                    highest_score = score

            tokens_true_case.append(best_token)

        tokens_true_case[0] = self.first_token_case(tokens_true_case[0])
        return tokens_true_case
