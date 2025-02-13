import pandas as pd
import streamlit as st
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import json
from helpers.funtions import get_grid

@st.cache_data
def data_preprocessing(items_df, orders_df, customers_df, ndays) -> pd.DataFrame:
    """
    Обрабатывает данные о заказах и клиентах, формируя агрегированную таблицу.
    """
    # Рассчитываем сумму заказа
    items_df['order_sum'] = items_df['price'] * items_df['order_item_id']
    items_df = items_df.groupby('order_id').agg({'order_sum': 'sum'})

    # Фильтруем невыполненные заказы
    orders_df = orders_df[~orders_df.order_status.isin(['canceled', 'created', 'unavailable'])]
    orders_df = orders_df[['order_id', 'customer_id', 'order_purchase_timestamp']]

    # Преобразуем дату покупки и считаем дни с последнего заказа
    orders_df['order_date'] = pd.to_datetime(orders_df['order_purchase_timestamp']).dt.date
    orders_df['days_delta'] = (orders_df['order_date'].max() - orders_df['order_date']).apply(lambda x: x.days)

    # Фильтруем заказы старше ndays
    orders_df = orders_df[orders_df.days_delta <= ndays]

    # Объединяем таблицы
    df = orders_df.merge(customers_df, on='customer_id', how='left')
    df = df.merge(items_df, on='order_id', how='left')[['customer_unique_id', 'order_date', 'order_sum', 'days_delta']]

    # Агрегируем по клиенту
    df = df.groupby("customer_unique_id", as_index=False).agg({"days_delta": ["min", "count"], "order_sum": "sum"})
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
                                         0, df[cut_col].max() + 1,
                                         (int(df[cut_col].max() * 0.1),
                                          int(df[cut_col].max() * 0.9)))
    else:
        range_min, range_max = st.slider(f"Выберете границы сегментации клиентов по параметру: '{text.lower()}'",
                                         0.0, df[cut_col].max() + 1,
                                         (df[cut_col].max() * 0.1,
                                          df[cut_col].max() * 0.9))

    df["groups"] = pd.cut(df[cut_col],
                          [-1, range_min, range_max, df[cut_col].max() + 2], right=False, retbins=False,
                          include_lowest=True,
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


def get_segmented_df(df: pd.DataFrame, segments: dict, r_col, f_col, m_col) -> pd.DataFrame:
    """
        Применяет сегментацию к данным по заданным параметрам RFM.
        """
    df = df.drop(columns=["groups"], errors='ignore')  # Удаляем столбец groups, если он есть

    for key, col in zip(["R", "F", "M"], [r_col, f_col, m_col]):
        df[key] = pd.cut(
            df[col],
            [-1, *st.session_state.get(key, []), df[col].max() + 2],
            right=False,
            labels=segments.get(key, [])
        )

    return df



@st.fragment
def print_results(df: pd.DataFrame, segments: dict):
    """
    Выводит результаты сегментации клиентов и визуализирует распределение данных.
    """

    def change(df, segments):
        st.session_state["df"] = get_segmented_df(df, segments, 'days_since_last_order', 'orders_count', 'order_sum')

    st.button("Применить настройки сегментации", on_click=change, args=(df, segments))
    st.subheader("Результаты сегментации клиентов")
    st.markdown("Сводная таблица с количеством клиентов в каждой категории")
    df = get_segmented_df(df, segments, 'days_since_last_order', 'orders_count', 'order_sum')

    # Получаем сегментированные данные
    data = st.session_state.get('df', df)

    # Строим сводную таблицу RFM
    pivot_table = pd.pivot_table(
        data=data[["R", "F", "M"]],
        index=["R", "F"],
        columns="M",
        aggfunc=lambda x: f"{len(x)} \n\r {len(x) / len(df.customer_unique_id):.2%}",
        fill_value="0 \n\r 0.00%"
    )
    st.table(pivot_table)

    st.markdown("#### Детальные данные сегментации")
    download_data = get_grid(data)
    st.download_button(
        "Скачать данные",
        data=download_data.get("data").to_csv().encode("utf-8"),
        mime="text/csv"
    )
    return st.session_state.get('df', df)
