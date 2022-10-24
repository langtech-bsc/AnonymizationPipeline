import shutil
from pathlib import Path

import spacy_streamlit
import streamlit as st

from anonymize import AllAnonym, LabelAnonym, RandomAnonym
from ingestors import Streamingestor
import json
from itertools import chain
import demo_utils as utl

from sensitive_identification.name_identifiers import SpacyIdentifier
from sensitive_identification.regex_identification import RegexIdentifier

# st.set_page_config(page_title="Anonimización de contenidos generados por usuarios")
st.set_page_config(page_title="Anonimización de contenidos generados por usuarios", layout="wide")

utl.inject_custom_images()
utl.inject_custom_html()
utl.inject_custom_css()
utl.inject_custom_js()

st.title("Demo de Anonimización Multilingüe")
# st.header("Anonimización multilingüe de contenidos generados por usuarios")

st.markdown(
    "Anonimizador para castellano y catalán de contenidos generados por usuarios en sistemas conversacionales, para limpiar o reemplazar la información personal que puedan contener. Se utilizan gramáticas y modelos neuronales.")


@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    unstructured_identifier = SpacyIdentifier("models/main_model")
    regex_identifier = RegexIdentifier("data/regex_definition.csv")
    ingestor = Streamingestor("")
    labels = set(chain(unstructured_identifier.get_labels(), regex_identifier.get_labels()))
    return {"unstructured": unstructured_identifier, "regex": regex_identifier, "ingestor": ingestor,
            "anonymizers": {"Random": RandomAnonym(), "Etiqueta": LabelAnonym(), "Inteligente": AllAnonym()},
            "labels": labels}


models = load_models()
labels = models["labels"]

st.markdown("""### Técnicas de anonimización:


#### Label
_label_ reemplaza la información sensible con una etiqueta que identifica su clase. 

> **Input**: "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689."

> **Anonymized**: "Hola, me llamo \<PER\> y vivo en \<LOC\>. Tel: \<TELEPHONE\>."

#### Random
_random_ reemplaza la información sensible con una con una cadena de texto aleatoria, que preserva la ortotipografía (mayúsculas o minúscules, etc.). 

> **Input**: "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689."

> **Anonymized**: "Hola, me llamo Dfkwa Mjzhnt y vivo en Ujflqo vc jaa Xvzqs 682. Tel: 441573591."

#### Intelligent
_intelligent_ reemplaza la información con substituciones a partir de gazetteers correspondientes a la etiqueta del tipo detectado. 

> **Input**: "Hola, me llamo María Salima y vivo en Carrer de las Rosas 123. Tel: 617753689."

> **Anonymized**: "Hola, me llamo Shakira Lois y vivo en carrer de Nicaragua 94. Tel: 211608837."

  """)

st.markdown('### Información detallada y código en el [repo GitHub](https://github.com/TeMU-BSC/AnonymizationPipeline)')
st.markdown('### Imagen Docker en el  [Docker Hub](https://hub.docker.com/r/bsctemu/anonymization-pipeline)')

text_input = st.text_area("Escribe el texto que deseas anonimizar")

uploaded_file = st.file_uploader("o sube un archivo", type=["doc", "docx", "txt"])

if uploaded_file is not None:
    file_input = uploaded_file.getvalue()
    text_input = file_input.decode("utf-8")

models["ingestor"].ingest_text(text_input)

anonymize = st.checkbox("Anonimizar")

registry = models["ingestor"].registry
models["unstructured"].identify_sensitive(registry)
models["regex"].identify_sensitive(registry)

doc = [{"text": registry.text,
        "ents": [{"start": span["start"], "end": span["end"], "label": span["label"]} for span in registry.spans]}]

spacy_streamlit.visualize_ner(doc, manual=True, show_table=False, labels=labels, title="Identificación de datos")

if anonymize:
    st.markdown("---")
    selection = st.selectbox("Método de anonimización", options=["Random", "Etiqueta", "Inteligente"])
    anonymizers = models["anonymizers"]
    anonimyzer = anonymizers[selection]
    models["ingestor"].anonymize_registries(anonimyzer)
    registry = models["ingestor"].registry
    doc = [{"text": registry.text,
            "ents": [{"start": span["start"], "end": span["end"], "label": span["label"]} for span in registry.spans]}]
    spacy_streamlit.visualize_ner(doc, manual=True, show_table=False, labels=labels, key="second",
                                  title="Anonomización")
    st.download_button(
        label="Download Anonymized json"
        , file_name="anonym.json"
        , mime="application/json"
        , data=json.dumps(doc[0])
    )
