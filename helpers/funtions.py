import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
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


@st.cache_data
def data_preprocessing(items_df, orders_df, customers_df, ndays) -> pd.DataFrame:
    items_df['order_sum'] = items_df['price'] * items_df['order_item_id']
    items_df = items_df.groupby('order_id').agg({'order_sum': 'sum'})
    # фильтруем невыполненные заказы
    orders_df = orders_df[~orders_df.order_status.isin(
        ['canceled', 'created', 'unavailable'])] \
        [['order_id', 'customer_id', 'order_purchase_timestamp']]
    orders_df['order_date'] = pd.to_datetime(orders_df['order_purchase_timestamp']) \
        .dt.date
    # считаем, сколько дней прошло с заказа
    orders_df['days_delta'] = (orders_df['order_date'].max() -
                               orders_df['order_date']) \
        .apply(lambda x: x.days)
    # фильтруем заказы возрастом более года
    orders_df = orders_df[orders_df.days_delta <= ndays]

    df = orders_df \
        .merge(customers_df, on='customer_id', how='left') \
        .merge(items_df, on='order_id', how='left') \
        [['customer_unique_id', 'order_date', 'order_sum', 'days_delta']]
    df = df.groupby("customer_unique_id", as_index=False) \
        .agg({"days_delta": ["min", "count"], "order_sum": "sum"})
    df.columns = ["customer_unique_id", "days_since_last_order", "orders_count", "order_sum"]
    return df


@st.fragment
def make_segmentation(df: pd.DataFrame, cut_col: str, x: str, y: str, segments: dict, text: str, key,
                      log_y: bool = False, exp_bins=False):
    segments = segments.get(key)

    def plt_joint(df: pd.DataFrame, x: str, y: str, segments: list, c=['green', 'gray', 'red']):
        cols = st.columns([1, 1, 1])
        for n, gr in enumerate(segments):
            data = df[df["groups"] == gr]
            if data.size == 0: continue
            g = sns.JointGrid(data=data, x=x, y=y, marginal_ticks=True)
            g.figure.suptitle(segments[n])
            if log_y:
                g.ax_joint.set(yscale="log")

            cax = g.figure.add_axes([.72, .6, .02, .2])
            g.plot_joint(
                sns.histplot, discrete=(True, False),
                cmap=f"light:{c[n]}", pmax=.8, cbar=True, cbar_ax=cax)
            g.plot_marginals(sns.histplot, element="step", color=c[n])
            # g.ax_marg_y.set_xscale("log")  # Логарифмическая шкала по X
            if log_y:
                g.ax_marg_x.set_yscale("log")  # Логарифмическая шкала по Y
            with cols[n]:
                st.pyplot(g.figure)

    # Создаём слайдер для выбора диапазона
    if df[cut_col].dtype == int:
        range_min, range_max = st.slider(f"Выберете границы сегментации клиентов по параметру: '{text.lower()}'",
                                         0, df[cut_col].max()+1,
                                         (int(df[cut_col].max() * 0.1),
                                          int(df[cut_col].max() * 0.9)))
    else:
        range_min, range_max = st.slider(f"Выберете границы сегментации клиентов по параметру: '{text.lower()}'",
                                         0.0, df[cut_col].max()+1,
                                         (df[cut_col].max() * 0.1,
                                          df[cut_col].max() * 0.9))

    df["groups"] = pd.cut(df[cut_col],
                          [-1, range_min, range_max, df[cut_col].max() + 2], right=False, retbins=False, include_lowest=True,
                          labels=segments)
    df_grouped = df.groupby("groups", observed=True)[cut_col].agg(
        ["count", lambda x: f"{len(x) / df.shape[0]:.1%}"]).reset_index()

    if exp_bins:
        bins = np.exp(np.histogram_bin_edges(df['order_sum'].apply('log'), 4 * int((df[cut_col].max()) ** (1.0 / 3))))
    else:
        bins = np.histogram_bin_edges(df[cut_col],
                                      bins=4 * int((df[cut_col].max()) ** (1.0 / 3)))

    # Вычисляем гистограмму
    hist_values, bin_edges = np.histogram(df[cut_col], bins=bins)

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
                # name=f"{bin_edges[i]:.0f} - {bin_edges[i + 1]:.0f} дней",
                hoverinfo="text",
                hovertext=f"{text}: {bin_edges[i]:.0f} - {bin_edges[i + 1]:.0f}<br>Число клиентов: {hist_values[i]}"
            )
        )

    # Настраиваем макет
    fig.update_layout(
        xaxis_title=text,
        yaxis_title="Число клиентов",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=200

    )
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Распределение клиентов по группам**")
        st.table(df_grouped.set_index("groups").T.reset_index(drop=True))
    with col2:
        st.plotly_chart(fig)
    plt_joint(df,
              x=x,
              y=y,
              segments=segments)
    st.session_state[key] = (range_min, range_max)


# with open('f.json', 'w') as f:
#     json.dump({"R":["Недавние клиенты", "Нерегулярные клиенты", "Потерянные клиенты"],
#                "F":["Очень редкие покупки", "Редкие покупки",  "Частые покупки"],
#                "M":["Маленькая сумма", "Средняя сумма", "Большая сумма"]}, fp=f, ensure_ascii=False)

def get_segments(fname: str, template_folder='data/templates/'):
    fname = template_folder + fname
    try:
        with open(fname, 'r') as f:
            j = json.load(f)
            return j
    except Exception as e:
        print(e)


def get_segmented_df(df: pd.DataFrame, segments: dict, r_col, f_col, m_col) -> pd.DataFrame:
    df = df.drop("groups", axis=1)
    for key, col in list(zip(["R", "F", "M"], [r_col, f_col, m_col])):
        df[key] = pd.cut(df[col],
                          [-1, *st.session_state.get(key), df[col].max() + 2], right=False, retbins=False,
                          labels=segments.get(key))
    return df

@st.fragment
def print_results(df, segments):
    def change(df, segments):
        st.session_state["df"] = get_segmented_df(df, segments, 'days_since_last_order', 'orders_count', 'order_sum')
    st.button("Применить настройки сегментации", on_click=change, args=(df, segments))
    st.subheader("4 Результаты сегментации")
    st.markdown("Ниже приведена сводная таблица с количеством клиентов, которые попали в каждую из категорий")
    df = get_segmented_df(df, segments, 'days_since_last_order', 'orders_count', 'order_sum')

    data = st.session_state.get('df', df)

    st.table(pd.pivot_table(data=data[["R", "F", "M"]], index=["R", "F"], columns="M",
                            aggfunc=lambda x: f"{len(x)} \n\r {len(x) / len(df.customer_unique_id):.2%}",
                            fill_value="0 \n\r0.00%"))

    st.dataframe(df, hide_index=True)
    return st.session_state.get('df', df)

def load_lottiefile(fname, pth ='./static/'):
    fname = pth + fname
    with open(fname, 'r') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(e)
            return None