import pandas as pd
import streamlit as st
import json


def read_template(fname: str, template_folder='data/templates/') -> str:
    fname = template_folder + fname
    template_text = "Данные не загружены"
    try:
        with open(fname, mode="r", encoding="utf-8") as f:
            template_text = f.read()
    except Exception as e:
        print(e)
    return template_text


@st.cache_data
def load_dataset(fname: str, datasets_folder='data/datasets/') -> pd.DataFrame:
    fname = datasets_folder + fname
    df = pd.DataFrame()
    try:
        df = pd.read_csv(fname, compression='gzip')
    except Exception as e:
        print(e)
    return df


def load_lottiefile(fname, pth='./static/'):
    fname = pth + fname
    with open(fname, 'r') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(e)
            return None
