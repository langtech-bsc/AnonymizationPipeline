# Data

This document will recover information about the data that is fed to the pipeline and the data that it produces. 

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

## Regex for pattern identification

The regex file used for the regex identifier (located inside the `data` directory), is expressed in csv format. 

The collumns are:
- Label name
- Rank (used for the merge of spans that have overlap, the smaller, the more precedence it has)
- Description (for internal usage)
- The Regex expression as a String

## Names and surnames for the Intelligent anonymization

Names and surnames are located in the `data` directory as well (under the `data/names/names_no_rep.txt` and `data/surnames.txt`). They are no repetition lists of the most common names of the kids born in Catalunya. 

Each line contains a single name/surname and they can be sorted or not. 
