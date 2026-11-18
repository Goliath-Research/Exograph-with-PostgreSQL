\set ON_ERROR_STOP on

SELECT p.category,
       SUM(oi.quantity::bigint * oi.unit_price_cents::bigint)::bigint AS revenue_cents
FROM commerce.orders AS o
JOIN commerce.order_items AS oi USING (order_id)
JOIN commerce.products AS p USING (sku)
WHERE o.ordered_at >= TIMESTAMPTZ '2026-01-01 00:00:00+00'
  AND o.ordered_at < TIMESTAMPTZ '2026-02-01 00:00:00+00'
  AND o.order_status IN ('PAID', 'SHIPPED')
GROUP BY p.category
ORDER BY p.category ASC
LIMIT 10;

SELECT order_id,
       COUNT(*) AS line_count,
       SUM(quantity::bigint * unit_price_cents::bigint)::bigint AS total_cents
FROM commerce.order_items
WHERE order_id = 101
GROUP BY order_id;
