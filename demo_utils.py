import shutil
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html


def inject_custom_images():
    STREAMLIT_STATIC_PATH = Path(st.__path__[0]) / 'static'
    IMAGE_PATH = (STREAMLIT_STATIC_PATH / "assets/custom-images")
    shutil.copytree("demo/assets/images", IMAGE_PATH, dirs_exist_ok=True)


def inject_custom_css():
    with open('demo/assets/css/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def inject_custom_js():
    with open('demo/assets/js/custom.js') as f:
        js = f'<script>{f.read()}</script>'
        html(js)


def inject_custom_html():
    with open('demo/assets/html/custom.html') as f:
        custom_html = f'{f.read()}'
        st.markdown(custom_html, unsafe_allow_html=True)
