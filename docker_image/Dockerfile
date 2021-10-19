FROM python:3.6.15-slim-bullseye

RUN mkdir /home/anonym

ADD anon_pipe.zip /home/anonym

WORKDIR /home/anonym

RUN apt-get update

RUN apt-get -y install unzip

RUN unzip anon_pipe.zip

RUN pip install -r requirements.txt

RUN python -m spacy download es_core_news_sm

RUN python -c 'from transformers import AutoTokenizer, AutoModel;tokenizer = AutoTokenizer.from_pretrained("BSC-TeMU/roberta-base-bne-capitel-ner-plus");model = AutoModel.from_pretrained("BSC-TeMU/roberta-base-bne-capitel-ner-plus")'
