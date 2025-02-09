import streamlit as st
from helpers.funtions import (read_template, load_dataset, data_preprocessing)
import altair as alt
import pandas as pd
import numpy as np
# ---Load data---
customers_df = load_dataset("olist_customers_dataset.csv")
orders_df = load_dataset("olist_orders_dataset.csv")
items_df = load_dataset("olist_order_items_dataset.csv")

with st.expander("Справка о RFM анализе"):
    st.markdown(read_template("about_rfm.md"))

st.markdown("""
Для демонстрации метода воспользуемся данными о продажах e-commerce компании,
взятыми из этого открытого [репозитория](https://github.com/erood/interviewqs.com_code_snippets/). Для этого нам потребуются файлы `olist_customers_dataset.csv`, `olist_orders_dataset.csv`, `olist_order_items_dataset.csv`.
В качестве инструмента анализа используем python библиотеку pandas.
""")

with st.expander("Описание таблиц и примеры исходных данных"):
    st.markdown(read_template("data_description.md"))
    st.divider()
    st.markdown("### Примеры исходных данных")
    st.subheader("list_customers_dataset")
    st.dataframe(data=customers_df.head(5))
    st.subheader("olist_orders_dataset")
    st.dataframe(data=orders_df.head(5))
    st.subheader("olist_order_items_dataset")
    st.dataframe(data=items_df.head(5))

# --- Section 1---
st.subheader("1 Выбор колонок и проверка данных")
st.markdown("""
Отберем в каждой из таблиц только нужные для данного вида анализа поля. Убедимся,
что в них не содержится пропусков, с помощью кода вида:
```python
pd.DataFrame.isna().sum()
""")

# ---Filter data---
customers_df = customers_df[['customer_id', 'customer_unique_id']]
orders_df_ = orders_df[['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp']]
items_df = items_df[['order_id', 'order_item_id', 'product_id', 'price']]

col1, col2, col3 = st.columns([4, 5, 4])
with col1:
    st.markdown("**customers_df**")
    st.caption("olist_customers_dataset")
    st.table(customers_df.isna().sum().rename('NaN'), )
with col2:
    st.markdown("**orders_df**")
    st.caption("olist_orders_dataset")
    st.table(orders_df_.isna().sum().rename('NaN'), )
with col3:
    st.markdown("**items_df**")
    st.caption("olist_order_items_dataset")
    st.table(items_df.isna().sum().rename('NaN'), )
# --- Section 2---
st.subheader("2 Предобработка и объединение исходных таблиц")
with st.expander("Предобработка, фильтрация и объединение таблиц"):
    st.markdown(read_template("data_preproc.md"))
df=data_preprocessing(items_df, orders_df, customers_df)
st.subheader("Посмотрим на полученный датафрейм")
st.dataframe(df, height=210)

with st.expander("Стратегия разбивки на RFM группы"):
    st.markdown(read_template("rfm_strategy.md"))

# Define two sliders for binding_rangeuser input
lower_slider = alt.binding_range(min=0, max=360, step=1, name='Lower Bound: ', debounce=1000)
upper_slider = alt.binding_range(min=0., max=360, step=1, name='Upper Bound: ', debounce=1000)

lower_selector = alt.param(name='LowerSelector', value=100, bind=lower_slider)
upper_selector = alt.param(name='UpperSelector', value=250, bind=upper_slider)

color = {'condition': [{'test': (alt.datum.days_since_last_order < lower_selector), 'value': 'green'},
{'test': (alt.datum.days_since_last_order > upper_selector), 'value': 'red'}], 'value': 'lightgray'}

# Create base chart with parameter binding
base = alt.Chart(df).add_params(lower_selector, upper_selector)

# Define color ranges
green = base.transform_filter(
    alt.datum.days_since_last_order < lower_selector).mark_bar(color='green').encode(
    x=alt.X('days_since_last_order:Q', bin=alt.Bin(maxbins=50), title="Days Since Last Order"),
    y=alt.Y('count()', title="Count"),

)

gray = base.transform_filter(
    (alt.datum.days_since_last_order >= lower_selector) &
    (alt.datum.days_since_last_order <= upper_selector)
).mark_bar(color="gray").encode(
    x=alt.X('days_since_last_order:Q', bin=alt.Bin(maxbins=50)),
    y=alt.Y('count()')
)

red = base.transform_filter(
    alt.datum.days_since_last_order > upper_selector
).mark_bar(color="red").encode(
    x=alt.X('days_since_last_order:Q', bin=alt.Bin(maxbins=50)),
    y=alt.Y('count()')
)

color = {'condition': [{'test': (alt.datum.days_since_last_order < lower_selector), 'value': 'green'},
{'test': (alt.datum.days_since_last_order > upper_selector), 'value': 'red'}], 'value': 'lightgray'}

facet_scatter = alt.Chart(df).mark_rect().encode(
    alt.X('orders_count:Q'),
    alt.Y('order_sum:Q').bin(maxbins=200),
    color=color,
)


# Combine charts
chart = (green + gray +red) | facet_scatter

# Display in Streamlit
st.altair_chart(chart, use_container_width=True)

values = st.slider(
'Select a range of values',
0.0, 100.0, (25.0, 75.0))
st.write('Values:', values)