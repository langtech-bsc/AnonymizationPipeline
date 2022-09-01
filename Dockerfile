FROM python:3.8-slim

RUN mkdir /home/anonym /home/anonym/data

COPY pipeline.py anonymize.py meta.py formatters.py name_identifiers.py regex_identification.py sensitive_identifier.py min_req.txt /home/anonym/

COPY data /home/anonym/data

WORKDIR /home/anonym

RUN apt-get update 

RUN python -m pip install -r min_req.txt

ENTRYPOINT ["python3", "pipeline.py"]

