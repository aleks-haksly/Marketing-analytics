import pandas as pd
import streamlit as st

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

@st.cache_data
def data_preprocessing(items_df, orders_df, customers_df)->pd.DataFrame:
    items_df['order_sum'] = items_df['price'] * items_df['order_item_id']
    items_df = items_df.groupby('order_id').agg({'order_sum': 'sum'})
    # фильтруем невыполненные заказы
    orders_df = orders_df[~orders_df.order_status.isin(
        ['canceled', 'unavailable'])] \
        [['order_id', 'customer_id', 'order_purchase_timestamp']]
    orders_df['order_date'] = pd.to_datetime(orders_df['order_purchase_timestamp']) \
        .dt.date
    # считаем, сколько дней прошло с заказа
    orders_df['days_delta'] = (orders_df['order_date'].max() -
                               orders_df['order_date']) \
        .apply(lambda x: x.days)
    # фильтруем заказы возрастом более года
    orders_df = orders_df[orders_df.days_delta <= 365]

    df = orders_df \
        .merge(customers_df, on='customer_id', how='left') \
        .merge(items_df, on='order_id', how='left') \
        [['customer_unique_id', 'order_date', 'order_sum', 'days_delta']]
    df = df.groupby("customer_unique_id", as_index=False) \
        .agg({"days_delta": ["min", "count"], "order_sum": "sum"})
    df.columns = ["customer_unique_id", "days_since_last_order", "orders_count", "order_sum"]
    return df



