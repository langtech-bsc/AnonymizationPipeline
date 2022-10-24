FROM python:3.8-slim

RUN mkdir /home/anonym /home/anonym/data /home/anonym/sensitive_identification

COPY pipeline.py demo_utils.py anonymize.py meta.py ingestors.py min_req.txt /home/anonym/

COPY models /home/anonym/models

COPY sensitive_identification /home/anonym/sensitive_identification/

COPY data /home/anonym/data

WORKDIR /home/anonym

RUN apt-get update 

RUN python -m pip install -r min_req.txt

ENTRYPOINT ["python3", "pipeline.py"]

