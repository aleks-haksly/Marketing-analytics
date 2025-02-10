import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from helpers.funtions import (read_template, load_dataset, data_preprocessing, plt_joint)
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
ndays = st.number_input("Выберите временой период в днях для анализа", min_value=30, max_value=None, value=365, step=1)
with st.expander("Предобработка, фильтрация и объединение таблиц"):
    st.markdown(read_template("data_preproc.md") % (ndays, ndays))
df=data_preprocessing(items_df, orders_df, customers_df, ndays)
st.subheader("Посмотрим на полученный датафрейм")
st.dataframe(df, height=210)

with st.expander("Стратегия разбивки на RFM группы"):
    st.markdown(read_template("rfm_strategy.md"))

import plotly.graph_objects as go

# Создаём слайдер для выбора диапазона
range_min, range_max = st.slider("Выберете границы сегментации клиентов по дате последней покупки", 0, ndays, (int(ndays*0.1), int(ndays*0.9)))

df["groups"] = pd.cut(df["days_since_last_order"], [-1, range_min, range_max, df["days_since_last_order"].max()+1], right=True,   retbins=False, labels=["недавние клиенты", "нерегулярные клиенты", "потерянные клиенты"])
df_grouped = df.groupby("groups", observed=True)["days_since_last_order"].agg(["count", lambda x: f"{len(x)/df.shape[0]:.1%}"]).reset_index()
st.dataframe(df_grouped.set_index("groups").T, hide_index=True)

bins = np.histogram_bin_edges(df["days_since_last_order"], bins=4 * int((df["days_since_last_order"].max()) ** (1.0 / 3)))

# Вычисляем гистограмму
hist_values, bin_edges = np.histogram(df["days_since_last_order"], bins=bins)

# Определяем цвета бинов
colors = [
    "green" if left_edge < range_min else "red" if left_edge >= range_max else "gray"
    for left_edge in bin_edges[:-1]
]

# Создаём фигуру в Plotly
fig = go.Figure()

# Добавляем столбцы гистограммы с кастомными hover
for i in range(len(hist_values)):
    fig.add_trace(
        go.Bar(
            x=[(bin_edges[i] + bin_edges[i + 1]) / 2],  # Центр бин-а
            y=[hist_values[i]],
            marker_color=colors[i],
            width=(bin_edges[i + 1] - bin_edges[i]) * 0.9,  # Ширина столбца
            name=f"{bin_edges[i]:.0f} - {bin_edges[i+1]:.0f} дней",
            hoverinfo="text",
            hovertext=f"Дней: {bin_edges[i]:.0f} - {bin_edges[i+1]:.0f}<br>Число клиентов: {hist_values[i]}"
        )
    )

# Настраиваем макет
fig.update_layout(
    title="Распределение клиентов по числу дней с последней покупки",
    xaxis_title="Дней с последней покупки",
    yaxis_title="Число клиентов",
    showlegend=False,
)
figs = plt_joint(df,
                 x='orders_count',
                 y='order_sum',
                 groups=["недавние клиенты", "нерегулярные клиенты", "потерянные клиенты"])
# Отображаем график в Streamlit

for fig in figs:
    st.pyplot(fig)
