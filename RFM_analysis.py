import streamlit as st
from streamlit_lottie import st_lottie
from helpers.funtions import (read_template, load_dataset, load_lottiefile, get_settings)
from helpers.RFM_functions import (data_preprocessing, make_segmentation, print_results)

col1, col2 = st.columns([2, 5])
with col1:
    logo = load_lottiefile("funnel.json")
    st_lottie(logo, speed=1.5, width=200, height=90)
with col2:
    st.header("RFM анализ")
# ---Load data---
customers_df = load_dataset("olist_customers_dataset.csv")
orders_df = load_dataset("olist_orders_dataset.csv")
items_df = load_dataset("olist_order_items_dataset.csv")
segments = get_settings("data/templates/RFM/segments.json")

with st.expander("Справка о RFM анализе"):
    st.markdown(read_template("RFM/about_rfm.md"))

st.markdown(read_template("RFM/intro.md"))

with st.expander("Описание таблиц и примеры исходных данных"):
    st.markdown(read_template("RFM/data_description.md"))
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
n_days = st.number_input("Выберем временой период в днях для анализа", min_value=30, max_value=None, value=365, step=1)
with st.expander("Предобработка, фильтрация и объединение таблиц"):
    st.markdown(read_template("RFM/data_preproc.md") % (n_days, n_days))
df = data_preprocessing(items_df, orders_df, customers_df, n_days)
st.markdown("#### Посмотрим на получившийся датафрейм")
st.dataframe(df, height=210)

with st.expander("Стратегия разбивки на RFM группы"):
    st.markdown(read_template("RFM/rfm_strategy.md"))

st.subheader("3 Подбор границ диапазонов для разбивки клиентов на группы")
st.markdown(
    "Используя слайдеры, подберем границы групп по каждому из RFM признаков, контролируя по графикам распределение значений по двум другим признакам в каждой из групп")
# R
make_segmentation(df, cut_col='days_since_last_order', x='orders_count', y='order_sum', segments=segments, log_y=True,
                  text='Число дней с последней покупки', key='R')
# F
make_segmentation(df, cut_col='orders_count', x='days_since_last_order', y='order_sum', segments=segments, log_y=True,
                  text='Число покупок', key='F')
# M
make_segmentation(df, cut_col='order_sum', x='orders_count', y='days_since_last_order', segments=segments, log_y=False,
                  text='Сумма покупок', key='M', exp_bins=True)
# segmentation results
print_results(df, segments)

st.subheader("4 Анализ полученных результатов")
with st.expander("Анализ полученных результатов и предлагаемые способы взаимодействия с клиентами"):
    st.markdown(read_template("RFM/conclusion.md"))
