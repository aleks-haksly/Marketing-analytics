Начнем с таблицы **items_df**, перемножим стоимость каждого товара
на его количество в заказе и предагрегируем данные на уровне заказа по полю *order_id*

```pyhon
items_df['order_sum'] = items_df['price'] * items_df['order_item_id']
items_df = items_df.groupby('order_id').agg({'order_sum': 'sum'})
```
В таблице **orders_df** поле *order_status* может иметь значения 'delivered', 'invoiced', 'shipped', 'processing', 'unavailable',
'canceled', 'created', 'approved'. Заказы со статусами 'unavailable' и 'canceled' в анализе мы учитывать не будем.
Кроме того, поле *order_purchase_timestamp* мы приведем к типу *date*, чтобы с ним можно было работать далее.
Будем считать "сегодняшней" датой в рамках RFM-анализа дату последнего заказа
в получившемся датафрейме. Исходя из этого, рассчитаем новый признак -
 количество дней, прошедших между датой заказа и "сегодняшним" днем.
Выберем временной период, на котором мы будем проводить RFM анализ.
Чаще всего для этого берется период длительностью один год от текущей даты,
но могут быть выбраны и другие периоды, в зависимости от отрасли и вида бизнеса.
Отфильтруем данные с учетом выбранного периода в 365 дней
```pyhon
# фильтруем невыполненные заказы
orders_df = orders_df[~orders_df.order_status.isin(
    ['canceled', 'unavailable'])] \
    [['order_id', 'customer_id', 'order_purchase_timestamp']]
orders_df['order_date'] = pd.to_datetime(orders_df['order_purchase_timestamp'])\
                            .dt.date
# считаем, сколько дней прошло с заказа							
orders_df['days_delta'] = (orders_df['order_date'].max() -
				orders_df['order_date'])\
				.apply(lambda x: x.days)
# фильтруем заказы возрастом более года
orders_df = orders_df[orders_df.days_delta <= 365]
```
Выполним join получившихся таблиц.
```pyhon
df = orders_df \
    .merge(customers_df, on='customer_id', how='left') \
    .merge(items_df, on='order_id', how='left')\
    [['customer_unique_id', 'order_date', 'order_sum', 'days_delta']]
```

Выполним агрегации, необходимые для RFM-анализа и посмотрим на результаты:
```pyhon
df = df.groupby("customer_unique_id", as_index=False)\
	   .agg({"order_sum": "sum", "days_delta": ["min", 'count']})
df.columns = ["customer_unique_id", "order_sum", "days_delta", "orders_count"]
```
