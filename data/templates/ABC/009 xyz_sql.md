```sql
WITH grouped_products AS (
    SELECT
        dr_ndrugs,
        dr_dat,
        SUM(dr_kol) AS amount
    FROM sales
    GROUP BY dr_ndrugs, dr_dat
),
all_dates AS (
    SELECT generate_series(
        (SELECT MIN(dr_dat) FROM sales),
        (SELECT MAX(dr_dat) FROM sales),
        '1 day'::interval
    )::date AS dates
),
all_products AS (
    SELECT DISTINCT dr_ndrugs AS products FROM sales
),
analytical_table AS (
    SELECT 
        d.dates, 
        p.products, 
        COALESCE(gp.amount, 0) AS amount  -- Заполняем нулями, чтобы учесть дни без продаж
    FROM all_dates d
    CROSS JOIN all_products p
    LEFT JOIN grouped_products gp 
        ON gp.dr_ndrugs = p.products 
        AND gp.dr_dat = d.dates
)
SELECT 
    products, 
    COALESCE(STDDEV(amount) / NULLIF(AVG(amount), 0), 0) * 100 AS cv_percent
FROM analytical_table
GROUP BY products
ORDER BY cv_percent DESC;
```