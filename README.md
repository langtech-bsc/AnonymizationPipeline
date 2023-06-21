# Anonymization pipeline
The anonymization pipeline is a library for performing sensitive data identification and posterior anonymization of the detected data in Spanish and Catalan user generated plain text. 

The performance of the pipeline heavily depends on the models used during the sensitive data identification process and the techniques used for anonymization reduce in different ways the re-identification probability. 

## Prerequisites

Make

[Docker](https://docs.docker.com/engine/install/ubuntu/)

[Docker compose](https://docs.docker.com/compose/install/)

[Git-LFS](https://git-lfs.github.com/)

# Structure of the Anonymization pipeline
The anonymization pipeline is composed of the following main structures:
- The runner (`pipeline.py`) which is used to run the identification, and (optional) anonymization with regular arguments in command line. 
- The Dockerfile for deploying the library in a Docker container
- The sensitive data identifiers:
	- Regular expression identifiers (`regex_identification.py`)
	- Named Entity recognition identifiers (`name_identifiers.py`)
- Formatters which ingest the data from different formats and transform it into the internal record/registries format for the functioning of the library (`formatters.py`)
- Anonymizers which implement different anonymization techniques (`anonymize.py`)
- Extra data used for the anonymization process (mainly gazetteers of names, locations and districts for better anonymization in the Barcelona city context).  

Extensions are encouraged and can be done in the formatters (to ingest new types of data) and the sensitive identifiers (for extra sensitive identification methods). In both files there are abstract classes that define the interfaces both implementation need to comply with. 

# Docker setup
For a simpler deployment we include a Dockerfile that can be used to deploy the library and run the pipeline without the need of setting up a custom python environment.

## Build the Docker image
To build the image simply run the following command in the directory that contains the Dockerfile
```bash
docker build --tag anonymization .
```
After building, you can inspect that the image is available by running: 
```bash
docker images
```

## Running the anonymization 
To run the anonymization pipeline image in a container we need to provide an input file (or directory), and output directory and the model directory to the container. To do so we will use mounted volumes. 

We might use the following structure for running the anonymization: (you can use the current project directory or a new one)
```
project_folder
	|- input/
		|- input_file_1
		|- input_file_2
		|- ...
	|- models/
		|- model_1
		|- model_2
		|- ...
	|- output/
```

With the previous structure for our anonymization process we can run the container with the following command from the project directory:

**NOTE:** The es_anonimization_core_lg and xx_ent_wiki_sm models are already included in the docker image and will run by default.
```bash
docker run --rm \                                                                                                                                                                                                               1 ↵
	-v $(pwd)/example_input:/home/anonym/example_input \
	-v $(pwd)/output:/home/anonym/output \
	anonymization -i example_input/plain_text/frases.txt -f plain -a intelligent -o output/output_test.jsonl
```
To run the pipeline with custom models, you have to mount the docker volume that contains the models directory.
```bash
docker run --rm \
	-v $(pwd)/input:/home/anonym/input \
	-v $(pwd)/models:/home/anonym/models \
	-v $(pwd)/output:/home/anonym/output \
	anonymization -m models/my_custom_model -i example_input/plain_text/frases.txt -f plain -a intelligent -o output/output_test.jsonl
```

The `$(pwd)` command is used to get the absolute path to the project folder and prevent path problems. 
The `--rm` argument for the `docker run` command is used to remove the container once the sensitive data identification and anonymization process has been performed in order to not accumulate containers and use up disk space. 

**This command will invoke the `pipeline.py` script, the arguments for the pipeline are detailed in the Usage section**. 


# Streamlit demo deployment (docker compose)

To deploy the streamlit demo run

```bash
  make deploy
```

# Local Python venv setup
If you want to run the pipeline manually (and possibly extend the code) it is better to setup a python virtual environment.

Check the python version, if you have python installed (python 3.8 onwards is encouraged) you can do so with: 
```bash
python --version
```
Prepare an isolated virtual environment:
```bash
python -m venv venv
```
Activate the virtual environment:
```bash
source venv/bin/activate
```
Install the dependencies of the library:
```bash
python -m pip install -r min_req.txt
```

Once you have the environment setup, you can run the pipeline with:
```bash
python pipeline.py [ARGS]
```

# Usage
The anonymization pipeline is a simple command argument script that performs 2 things sensitive identification of data in plain text and (optional) anonymization of the identified data. 

All commands here use the `pipeline.py` but the arguments are the same for the Docker setup since the docker image's entry point is the `pipeline.py` script (just omit the word `pipeline.py`and the arguments should be the same). 

To display the help of the arguments:
``` bash
python pipeline.py --help
```
Which will display something like: 
```
usage: pipeline.py [-h] -i INPUT [-m MODEL] [-t {spacy,huggingface}] [-f {plain,jsonl,doccano}] [-a {label,random,intelligent,none}] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File containing the original text with a context per line. (default: None)
  -m MODEL, --model MODEL
                        Path to the model that is going to be used (default: ./models/main_model)
  -t {spacy,huggingface}, --type_of_model {spacy,huggingface}
                        The type of model that is going to be used for the NER recognition phase (default: spacy)
  -f {plain,jsonl,doccano}, --format {plain,jsonl,doccano}
                        Format of the input file (default: plain)
  -a {label,random,intelligent,none}, --anonym_method {label,random,intelligent,none}
                        Anonymization technique that is going to be performed over the sensitive identified data (default: none)
  -o OUTPUT, --output OUTPUT
                        File to which the save action is performed (default: output/output.txt)
```

Example:
```bash
python pipeline.py -i example_input/plain_text/frases.txt -m models/ca_anonimization_core_lg models/xx_ent_wiki_sm -f plain -a intelligent -o output/output_test.jsonl -t spacy spacy
```

The details about the functioning of each argument and the formats of the input and output files are detailed below. 

The same arguments as in the example can be used in the Docker setup since the structure of the volumes has the **input**, **output** and **models** directories. 

## Anonymization techniques
There are 3 anonymization techniques that can be performed now: _label_, _random_, _intelligent_ and _none_. 

### None
The last one (_none_) doesn't perform any anonymization, but can be used to inspect the entities and sensitive data the models for sensitive identification detect. 

### Label
The _label_ method replaces sensitive data for the label which the models have detected. 
For example the following could be an anonymization performed using this technique:

> **Input**: "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689."
> **Anonymized**: "Hola, me llamo \<PER\> y vivo en \<LOC\>. Tel: \<TELEPHONE\>."

This technique is good to see the detection at a glance, but suffers from the problem that data missed by the identification phase is simple to detect by reading the anonymized output (since it is certainly not replaced by an obvious label). 

### Random
The _random_ method replaces sensitive data for a random string that preserves the "structure" of the string (i.e. upper and lower cases, length and type of characters). 
For example the following could be an anonymization performed using this technique:

> **Input**: "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689."
> **Anonymized**: "Hola, me llamo Dfkwa Mjzhnt y vivo en Ujflqo vc jaa Xvzqs 682. Tel: 441573591."

This technique is useful for analyzing the results with statistical tests that take into account the structure of the words, but ignore the specific characters. 
However, though less notorious, it suffers from the same problem as the _label_ method, in which identifying the things that the sensitive data detection phase missed is simple. 

### Intelligent
The _intelligent_ method replaces the data for substitutes that come from gazetteers of the corresponding label. 
For example the following could be an anonymization performed using this technique:

> **Input**: "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689."
> **Anonymized**: "Hola, me llamo Shakira Lois y vivo en carrer de Nicaragua 94. Tel: 211608837."

This technique is the safest one, since the data that is being replaced is of the same nature as the original data, identifying sensitive data that has been missed by the detection phase is far harder. 

## Input format
There are 3 input formats that can be used to ingest text and perform the sensitive data identification and the anonymization phases. 

In al formats the text to be treated must contain a full context in each line. If the text is multiline, the line jumps can be replaced by `\n` or each line will be treated as a separate context. 
Examples of the plain text format and the minimal jsonl format can be found in the `example_input` directory.

### Plain text format
Each line in the text file is a context that might contain sensitive data. Each context will be treated separately. 

**Example**:
```
Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689.
Nuestra empresa está en la Calle Aragón 543. \nMi NIE es U7698663W.
...
```

### jsonl format
The jsonl format is the one used in Spacy and Prodigy to label data. It has a compact and useful structure. 
The file has the `.jsonl` extension and has a json object in each line. 
The json of each line has the following format
```json
{"text": "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689.", "spans":[],"meta":{"ID":23434, ...}}
```
This format is simpler to manipulate than the plain text format and is easier to trace the execution of the anonymization process with it. We encourage the usage of this format instead of plain text. 

The `meta` attribute is an object that must contain an `ID` for traceability and it can have any other fields of metadata that one wants to include. 

Multi-line texts can be included with the `\n` symbol. 

**Example**:
```json
{"text": "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689.", "spans":[],"meta":{"ID":1, "origin": "orig1", "date":"2022/05/15"}}
{"text": "Nuestra empresa está en la Calle Aragón 543. \nMi NIE es U7698663W.", "spans":[],"meta":{"ID":2, "origin": "orig1", "date":"2022/05/15"}}
...
```


## Output format
The output of the pipeline follows the **jsonl** format described above. 

The output will contain the text (anonymized with the corresponded technique) and the spans of the sensitive data that has been identified as well as any metadata inserted in the `meta` attribute. 

**Example**:
```json
{"text": "Hola, me llamo <PER> y vivo en <LOC>. Tel: <TELEPHONE>.\n", "spans": [{"start": 15, "end": 20, "label": "PER", "rank": 0}, {"start": 31, "end": 36, "label": "LOC", "rank": 0}, {"start": 43, "end": 54, "label": "TELEPHONE", "rank": 1}], "meta": {"ID":1, "origin": "orig1", "date":"2022/05/15"}}
{"text": "Nuestra empresa está en la <LOC>. \\nMi NIE es <ID>.\n", "spans": [{"start": 27, "end": 32, "label": "LOC", "rank": 0}, {"start": 46, "end": 50, "label": "ID", "rank": 2}], "meta": {"ID":2, "origin": "orig1", "date":"2022/05/15"}}
...
```

## Named Entity Recognition models

The sensitive data identification is performed mainly by 2 models, a regex model (which has a big set of regular expressions in `sensitive_regex.py`) and a Named Entity Recognition (NER) model. 

The first model is good at finding regular patterns, like phone numbers (though people can write them down in unimaginable ways), but is not good for finding locations, people's names nor other soft data that is not regular. 

The second model is better at finding the things that are not regular that the regex model fails to identify. 

Currently we allow for 2 type of models for NER, Spacy models (which are lightweight and are more flexible) and Huggingface RoBERTa models (which are larger and achieve better results in certain conditions, but are less flexible and are better suited for environments in which one can use GPUs). 

Any Spacy model trained for the NER task can be used for the sensitive data detection, but those trained for identifying specific sensitive data are more suited. 

Models available for download and install at:

- https://huggingface.co/PlanTL-GOB-ES/ca_anonimization_core_lg

- https://huggingface.co/spacy/xx_ent_wiki_sm

Clone them under the models/ directory or reference them if installing on envs via pip.

## Customizing Regex
If specific regex expressions or patterns are to be recognized, one can replace the regex definition of the regex model providing a new regex definition file. 

The file used for determining the regex expressions that are to be identified is located under `data/regex_definition.csv`.

For example if we put the new csv file defining the regex patters under `models/regex/custom_regex.csv`, the `--regexes` argument can be used with the corresponding path to use the custom expressions instead of the default ones. 

## Restricting Labels to be treated as sensitive
Often models for NER and regex files (like the default one) contain data that we don't want to treat as sensitive. To prevent the identification (and posterior anonymization of such labels), one can use the `--labels` argument passing a simple text file with a list of labels to be treated as sensitive. 

An example fo such list is provided under `example_input/labels/test_labels.txt`

## Arguments with configuration files
Arguments to the script can be passed by using configuration files. 
The argument for passing the configuration path is `-c`. This allows for reusing the same configuration across different experiments and setups. It also helps wit organization and reproducibility (since configuration files are easier to share than command arguments). 

An example of the configuration file can be found in: `example_config/`. 

All arguments specified in the configuration file can be overriden by commandline arguments, thus allowing for using a base configuration and running different executions by changing the arguments in the commandline. 

## License

This project is licensed under the Apache License, Version 2.0. (https://www.apache.org/licenses/LICENSE-2.0)
