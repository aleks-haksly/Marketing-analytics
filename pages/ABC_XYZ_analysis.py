import streamlit as st
import pandas as pd

from helpers.funtions import (read_template, load_lottiefile)
from helpers.ABC_functions import select, print_abc_results, print_xyz_results
from streamlit_lottie import st_lottie

st.set_page_config(layout="wide")

col1, col2 = st.columns([1, 4])
with col1:
    logo = load_lottiefile("laptop.json")
    st_lottie(logo, speed=1.5, width=200, height=90)
with col2:
    st.header("Многомерный ABC + XYZ анализ")
st.subheader("1. Многомерный ABC анализ")
with st.expander("Справка о ABC анализе"):
    st.markdown(read_template("ABC/001 about_abc.md"))
st.markdown(read_template("ABC/002.md"))
with st.expander("Описание и пример исходных данных"):
    st.markdown(read_template("ABC/003 table_desc.md"))
    st.markdown("Пример данных:")
    st.table(select("SELECT dr_dat, dr_ndrugs, dr_kol, dr_croz, dr_czak, dr_sdisc FROM apteka.sales LIMIT 5"))
with st.expander("Подключение в PostgreSQL"):
    st.markdown(read_template("ABC/004 sql engine.md"))
with st.expander("SQL код, группирующий товары по уникальному наименованию товарной позиции и выполняющий агрегации"):
    st.markdown(read_template("ABC/005 abc_sql.md"))
st.markdown(read_template("ABC/006 abc_variation.md"))
print_abc_results()
st.markdown("#### Выводы по многомерному ABC-анализу продаж товаров аптечной сети")
with st.expander("Выводы и рекомендации"):
    st.markdown(read_template("ABC/007 abc_summary.md"))

st.subheader("2. XYZ анализ")
with st.expander("Справка о XYZ анализе"):
    st.markdown(read_template("ABC/008 about_xyz.md"))
with st.expander("SQL код для анализа вариативности спроса"):
    st.markdown(read_template("ABC/009 xyz_sql.md"))
print_xyz_results()