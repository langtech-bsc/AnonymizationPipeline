import spacy_streamlit
import streamlit as st
from anonymize import AllAnonym, LabelAnonym, RandomAnonym
from ingesters import StreamIngester
import json
from itertools import chain

from sensitive_identification.name_identifiers import SpacyIdentifier
from sensitive_identification.regex_identification import RegexIdentifier

st.title("Demo de Anonimizador")

@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    unstructured_identifier = SpacyIdentifier("./models/model_ca_core_lg_iris_05_31")
    regex_identifier = RegexIdentifier("data/regex_definition.csv")
    ingester = StreamIngester("")
    labels = set(chain(unstructured_identifier.get_labels(), regex_identifier.get_labels()))
    return {"unstructured": unstructured_identifier, "regex":regex_identifier, "ingester":ingester, "anonymizers": {"Random": RandomAnonym(), "Etiqueta":LabelAnonym(), "Inteligente": AllAnonym()}, "labels": labels}

models = load_models()
labels = models["labels"]

text_input = st.text_area("Escribe el texto que deseas anonimizar")


uploaded_file = st.file_uploader("o sube un archivo", type=["doc", "docx", "txt"])

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
    anonymizers = models["anonymizers"]
    anonimyzer = anonymizers[selection]
    models["ingester"].anonymize_registries(anonimyzer)
    registry = models["ingester"].registry
    doc = [{"text": registry.text, "ents": [{"start": span["start"], "end": span["end"], "label":span["label"]} for span in registry.spans]}]
    spacy_streamlit.visualize_ner(doc, manual=True, show_table=False, labels=labels, key="second", title="Anonymización")
    st.download_button(
        label="Download Anonymized json"
        , file_name="anonym.json"
        , mime="application/json"
        , data=json.dumps(doc[0])
    )

