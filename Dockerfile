FROM python:3.8-slim

RUN mkdir /home/anonym

COPY pipeline.py meta.py data formatters.py name_identifiers.py regex_identification.py sensitive_identifier.py sensitive_regex.py min_req.txt /home/anonym/

WORKDIR /home/anonym

RUN apt-get update 

RUN python -m pip install -r min_req.txt

ENTRYPOINT ["python3", "pipeline.py"]

