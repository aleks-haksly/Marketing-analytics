WITH grouped_products AS (
    SELECT
        dr_ndrugs,
        DATE_TRUNC('week', dr_dat)::date AS dr_dat,
        SUM(dr_kol) AS amount
    FROM apteka.sales
    GROUP BY dr_ndrugs, DATE_TRUNC('week', dr_dat) 
),
all_dates AS (
    SELECT generate_series(
        (SELECT MIN(DATE_TRUNC('week', dr_dat)::date) FROM apteka.sales), 
        (SELECT MAX(DATE_TRUNC('week', dr_dat)::date) FROM apteka.sales),
        '7 days'::interval
    ) AS dates
),
all_products AS (
    SELECT DISTINCT dr_ndrugs AS products FROM apteka.sales
),
analytical_table AS (
    SELECT 
        d.dates, 
        p.products, 
        COALESCE(gp.amount, 0) AS amount 
    FROM all_dates d
    CROSS JOIN all_products p
    LEFT JOIN grouped_products gp 
        ON gp.dr_ndrugs = p.products 
        AND gp.dr_dat = d.dates
)
SELECT 
    products as "Наименование", 
    COALESCE(STDDEV(amount) / NULLIF(AVG(amount), 0), 0) AS "Вариативность"
FROM analytical_table
GROUP BY "Наименование"
ORDER BY "Вариативность" DESC;