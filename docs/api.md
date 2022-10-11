# DEMO api

## Manual executionof the demo (local environment)

Once generated the Python virtual environment with the requirements for the execution of the Anonymization Pipeline, one can deploy the demo api with the following command: 

```
streamlit run api.py
```

The model that is usde is specified in the `api.py` file, but can be changed for a different model. 

## Streamlit demo deployment (docker compose)

To deploy the streamlit demo run

```bash
  make deploy
```
