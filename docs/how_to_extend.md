# How to extend the anonymization pipeline to make it perform better

There are different ways in which to extend the anonymization pipeline. Some include modifying small sections of the code, but others only need for external files (files that are "used" by the pipeline) to be modified. 

## Using a different NER model (no-code)

The NER model can be simply changed by adding it to the `models` directory and using the path to the model in the pipeline argument or in the configuration file. 

These NER model can be trained with specific data for the domain of the documents to be anonymized or it can be a generic NER model. 

Currently the models can be either a Spacy NER model or a Huggingface RoBERTa model. 

## Using multiple NER models (no-code)

The pipeline allows for the usage of multiple NER models as input. 

If more than one model is passed to the pipeline, each model will be executed over the content of the documents and de spans identified for each model will be merged when there is conflict between them. 

The easiest way to improve the performance of the model is to use multiple NER models trained for different types of documents. 

## Change the Regex expression (no-code)

The regex model is the easiest to extend by writing new expressions in the `data/regex_definitions.csv` file. 

Each domain tends to have custom expressions that follow specific patterns and thus can be added to this list of expressions. 

## Add ingestor (needs code)

Ingestors are the classes used for ingesting the documents in the input file. 

They can be extended by implementing a new ingestor extending the `Ingestor` class en redefining the following methods: 
- `__init__(self, input_file : str)` which is the constructor and recieves the path to the file to be ingested.
    - This method can be implemented by calling the super class constructor (which will read the input file line by line). 
    - **Note**: All ingestors are *eager*. This means that they process all documents in the input file when initialized
- `registryFactory(cls, line: str) -> Registry` which is the method that takes a single line in the input file (which should be a context) and transforms it into a `Registry` (class used for maintaining the text and spans in pipeline)
