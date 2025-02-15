import streamlit as st
import pandas as pd

from sqlalchemy import create_engine, text
from helpers.funtions import get_grid, read_sql


@st.cache_data
def select(sql: str) -> pd.DataFrame:
    """Выполняет SQL-запрос и возвращает результат в виде DataFrame.
    Args:
        sql (str): SQL-запрос
    Returns:
        pd.DataFrame: Результат запроса
    """
    supabase_connection_string = st.secrets.get("SUPABASE")
    if not supabase_connection_string:
        raise ValueError("SUPABASE environment variable is not set")

    engine = create_engine(supabase_connection_string)
    sql = text(sql)

    return pd.read_sql(sql, engine)

@st.fragment
def print_abc_results():
    """Выводит результаты классификации товаров"""

    def change():
        option = dict(zip(['A', 'B', 'C'], map(int, st.session_state["selected_option"].split("-"))))
        st.session_state["data"] = select(read_sql("ABC/abc.sql").format(**option))


    if "data" not in st.session_state:
        option = dict(zip(['A', 'B', 'C'], map(int, st.session_state.get("selected_option", "80-15-5").split("-"))))
        st.session_state["data"] = select(read_sql("ABC/abc.sql").format(**option))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### Результат классификации товаров:")
    with col2:
        st.selectbox(
            "H",
            ("80-15-5", "70-20-10", "50-30-20"),
            label_visibility="collapsed",
            on_change=change, key="selected_option")

    # Берем данные из session_state
    abc_grid = get_grid(st.session_state["data"], height=200)
    st.markdown("#### Сводная таблица для оценки количества товаров в каждой группе")
    st.table(pd.pivot_table(
        data=abc_grid.data[["По числу проданных позиций", "По прибыли с позиции", "По выручке с позиции"]],
        columns="По числу проданных позиций",
        index=["По прибыли с позиции", "По выручке с позиции"],
        aggfunc=lambda x: len(x),
        fill_value=0,
        observed=False, margins=True, margins_name='Всего'
    ).rename(columns={"A": "По числу проданных позиций: A",
                      "B": "По числу проданных позиций: B",
                      "C": "По числу проданных позиций: C"}).reset_index(), )


@st.fragment
def print_xyz_results():
    """Выводит результаты классификации товаров"""
    params = {
        "columnDefs": [
            {"field": "Наименование"},
            {
                "field": "Вариативность",
                "valueFormatter": "x = (value * 100).toFixed(1) + '%'; return x;"
            }
        ]
    }
    def change():
        if st.session_state["selected_option_xyz"] == "day":
            st.session_state["xyz_data"] = select(read_sql("ABC/xyz.sql"))
        else:
            st.session_state["xyz_data"] = select(read_sql("ABC/xyz_week.sql"))

    if "xyz_data" not in st.session_state:
        st.session_state["xyz_data"] = select(read_sql("ABC/xyz.sql"))

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### Результат классификации товаров:")
    with col2:
        st.selectbox(
            "H",
            ("day", "week"),
            label_visibility="collapsed",
            on_change=change, key="selected_option_xyz")

    # Берем данные из session_state
    xyz_grid = get_grid(st.session_state["xyz_data"],  **params, height=200)

