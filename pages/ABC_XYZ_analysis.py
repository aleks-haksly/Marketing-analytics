import streamlit as st
from helpers.funtions import (read_template, load_dataset, load_lottiefile)
from streamlit_lottie import st_lottie

col1, col2 = st.columns([2, 5])
with col1:
    logo = load_lottiefile("laptop.json")
    st_lottie(logo, speed=1.5, width=200, height=90)
with col2:
    st.header("ABC XYZ Анализ")