from unittest import case
import spacy_streamlit
import streamlit as st
from anonymize import AllAnonym, LabelAnonym, RandomAnonym
from formatters import StreamIngester

from name_identifiers import SpacyIdentifier
from regex_identification import RegexIdentifier

labels = [
        "EMAIL",
        "FINANCIAL",
        "ID",
        "LOC",
        "MISC",
        "ORG",
        "PER",
        "TELEPHONE",
        "VEHICLE",
        "ZIP", 
        "CARD", 
        "LICENSE_PLATE"
    ]

st.title("Demo de Anonimizador")

@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    unstructured_identifier = SpacyIdentifier("./tmp/models/model_ca_core_lg_iris_05_31")
    regex_identifier = RegexIdentifier("data/regex_definition.csv")
    ingester = StreamIngester("")
    return {"unstructured": unstructured_identifier, "regex":regex_identifier, "ingester":ingester}

models = load_models()

text_input = st.text_area("Escribe el texto que deseas anonimizar")


uploaded_file = st.file_uploader("o sube un archivo", type=["doc", "docx", "pdf", "txt"])

if uploaded_file is not None:
    file_input = uploaded_file.getvalue()
    text_input = file_input.decode("utf-8")

models["ingester"].ingest_text(text_input)

anonymize = st.checkbox("Anonimizar")



registry = models["ingester"].registry
models["unstructured"].identify_sensitive(registry)
models["regex"].identify_sensitive(registry)

doc = [{"text": registry.text, "ents": [{"start": span["start"], "end": span["end"], "label":span["label"]} for span in registry.spans]}]

spacy_streamlit.visualize_ner(doc, manual=True, show_table=False, labels=labels, title="Identificación de datos")

if anonymize:
    st.markdown("---")
    selection = st.selectbox("Método de anonimización", options=["Random", "Etiqueta", "Inteligente"])
    anonymizers = {"Random": RandomAnonym(), "Etiqueta":LabelAnonym(), "Inteligente": AllAnonym()}
    anonimyzer = anonymizers[selection]
    models["ingester"].anonymize_registries(anonimyzer)
    registry = models["ingester"].registry
    doc = [{"text": registry.text, "ents": [{"start": span["start"], "end": span["end"], "label":span["label"]} for span in registry.spans]}]
    spacy_streamlit.visualize_ner(doc, manual=True, show_table=False, labels=labels, key="second", title="Anonymización")

