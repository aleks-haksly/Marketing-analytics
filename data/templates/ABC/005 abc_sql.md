```sql
-- Сгруппируем товары по уникальному наименованию товарной позиции и выполним необходимые агрегации
with product_grouped as (
select
  dr_ndrugs, sum(dr_kol) as amounts, -- число продаж товара
  sum((dr_croz - dr_czak) * dr_kol - dr_sdisc) as pdofit_sum, -- прибыль с товарной позиции с учетом дисконта
  sum(dr_croz * dr_kol - dr_sdisc) as revenue_sum -- выручка с товарной позиции с учетом дисконта
from
  apteka.sales
group by dr_ndrugs
)
-- Выполним ABC анализ по каждому из посчитанных призаков (A-B-C  => 80-15-5%)
select product_grouped.dr_ndrugs as "Наименование товарной позиции",
case
    when sum(product_grouped.amounts) over (order by amounts desc) <= (select sum(dr_kol) * 0.8 from apteka.sales) then 'A'
    when sum(product_grouped.amounts) over (order by amounts desc) <= (select sum(dr_kol) * 0.95 from apteka.sales) then 'B'
    else 'C'
end as "По числу проданных позиций",
case
    when sum(product_grouped.pdofit_sum) over (order by pdofit_sum desc) <= (select sum((dr_croz - dr_czak) * dr_kol - dr_sdisc)* 0.8 from apteka.sales) then 'A'
    when sum(product_grouped.pdofit_sum) over (order by pdofit_sum desc) <= (select sum((dr_croz - dr_czak) * dr_kol - dr_sdisc)* 0.95 from apteka.sales) then 'B'
    else 'C'
end as "По прибыли с позиции",
case
    when sum(product_grouped.revenue_sum) over (order by revenue_sum desc) <= (select sum(dr_croz * dr_kol - dr_sdisc)* 0.8 from apteka.sales) then 'A'
    when sum(product_grouped.revenue_sum) over (order by revenue_sum desc) <= (select sum(dr_croz * dr_kol - dr_sdisc)* 0.95 from apteka.sales) then 'B'
    else 'C'
end as "По выручке с позиции"

from product_grouped
```