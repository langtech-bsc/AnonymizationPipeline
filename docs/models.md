# Models

There are 2 types of model used for identifying the sensitive data, Regex models and NER models. 

The first are in charge of capturing the structured things that follow a pattern for specific data (such as telephones, IDs for different contexts and credit card information). 
The second are in charge of detecting the sensitive spans that don't follow a specific pattern but which can be infered from the context that surround the span and the words that compose it (for example names, addresses, etc). 

## NER Models

NER models detect spans of sensitive data based on the knowledge that they've learned during training. 

In the Anonymization pipeline [Spacy NER](https://spacy.io/usage/linguistic-features#named-entities) models and [HuggingFace's RoBERTa](https://huggingface.co/docs/transformers/model_doc/roberta) models can be used to identify sensitive spans. 

They must be trained to detect the kind of sensitive data for the concrete use that one want to use it in, but they can learn to identify most things with few examples. 

Having a better anonymization result is oftenmost a consquence of having a better NER model. 

## Regex models

The regex models pick up the definitions of the custom regex for the anonymization (in most contexts one wants to use custom regex) from the file `data/regex_definition.csv`. 

Normal regex for different things are collected in the original definition, but one can modify to extend or supress some of the regex expressions. 