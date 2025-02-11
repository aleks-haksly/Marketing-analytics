### Описание таблиц
#### olist_customers_dataset.csv
**Таблица с уникальными идентификаторами пользователей**  
- `customer_id` — позаказный идентификатор пользователя.  
- `customer_unique_id` — уникальный идентификатор пользователя (аналог номера паспорта).  
- `customer_zip_code_prefix` — почтовый индекс пользователя.  
- `customer_city` — город доставки пользователя.  

#### olist_orders_dataset.csv  
**Таблица заказов**  
- `order_id` — уникальный идентификатор заказа (номер чека).  
- `customer_id` — позаказный идентификатор пользователя.  
- `order_status` — статус заказа.  
- `order_purchase_timestamp` — время создания заказа.  
- `order_approved_at` — время подтверждения оплаты.  
- `order_delivered_carrier_date` — передача заказа в логистическую службу.  
- `order_delivered_customer_date` — время доставки.  
- `order_estimated_delivery_date` — обещанная дата доставки.  

#### olist_order_items_dataset.csv  
**Товарные позиции в заказах**  
- `order_id` — уникальный идентификатор заказа.  
- `order_item_id` — идентификатор товара в заказе.  
- `product_id` — идентификатор товара (аналог штрихкода).  
- `seller_id` — идентификатор продавца.  
- `shipping_limit_date` — крайний срок передачи заказа логистическому партнеру.  
- `price` — цена за единицу товара.  
- `freight_value` — вес товара.