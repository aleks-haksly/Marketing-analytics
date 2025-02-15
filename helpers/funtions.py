import pandas as pd
import streamlit as st
import json
from st_aggrid import GridOptionsBuilder, AgGrid, DataReturnMode
# install streamlit-aggrid-bugfix==0.3.4.post4


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

def read_sql(fname: str, params=None, sql_folder='data/SQL/') -> str:
    fname = sql_folder + fname
    sql_text = "SELECT 'Sql script not found'"
    try:
        with open(fname, mode="r", encoding="utf-8") as f:
            sql_text = f.read()
    except Exception as e:
        print(e)
    if params:
        sql_text = sql_text.format(**params)
    return sql_text


def get_grid(df: pd.DataFrame, **params):
    """
    Создаёт интерактивную таблицу с возможностью сортировки и фильтрации.
    """
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    grid_options = gb.build()
    if params:
        grid_options.update(**params)
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        width="100%",
        fit_columns_on_grid_load=True,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED
    )
    return grid_response

def get_settings(fname: str, template_folder='data/templates/', encoding=None):
    fname = template_folder + fname
    try:
        with open(fname, 'r', encoding=encoding) as f:
            j = json.load(f)
            return j
    except Exception as e:
        print(e)