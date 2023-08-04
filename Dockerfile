FROM python:3.8-slim

RUN mkdir /home/anonym /home/anonym/data /home/anonym/sensitive_identification

WORKDIR /home/anonym

RUN apt-get update 

COPY min_req.txt /home/anonym/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r min_req.txt
RUN pip install https://huggingface.co/PlanTL-GOB-ES/es_anonimization_core_lg/resolve/main/es_anonimization_core_lg-any-py3-none-any.whl
RUN pip install https://huggingface.co/spacy/xx_ent_wiki_sm/resolve/main/xx_ent_wiki_sm-any-py3-none-any.whl
RUN python -m nltk.downloader punkt


COPY pipeline.py anonymize.py meta.py ingestors.py /home/anonym/

COPY models /home/anonym/models

COPY truecaser /home/anonym/truecaser/

COPY sensitive_identification /home/anonym/sensitive_identification/

COPY data /home/anonym/data

ENTRYPOINT ["python3", "pipeline.py"]

