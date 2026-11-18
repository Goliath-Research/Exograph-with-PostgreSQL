\set ON_ERROR_STOP on

-- Run as exograph_runtime on the disposable fixture database only.
BEGIN;
DO $verify$
DECLARE
    order_total bigint;
BEGIN
    IF current_user <> 'exograph_runtime' OR current_database() <> 'exograph_commerce' THEN
        RAISE EXCEPTION 'Use exograph_runtime on exograph_commerce';
    END IF;

    IF (SELECT count(*) FROM commerce.customers) <> 2
       OR (SELECT count(*) FROM commerce.products) <> 2
       OR (SELECT count(*) FROM commerce.orders) <> 2
       OR (SELECT count(*) FROM commerce.order_items) <> 3 THEN
        RAISE EXCEPTION 'Unexpected fixture row counts';
    END IF;

    SELECT sum(quantity::bigint * unit_price_cents) INTO order_total
    FROM commerce.order_items WHERE order_id = 101;
    IF order_total IS DISTINCT FROM 3200 THEN
        RAISE EXCEPTION 'Order 101: expected 3200 cents, got %', order_total;
    END IF;

    BEGIN
        UPDATE commerce.orders SET order_status = order_status WHERE order_id = 101;
        RAISE EXCEPTION 'Runtime UPDATE unexpectedly succeeded';
    EXCEPTION WHEN insufficient_privilege THEN
        RAISE NOTICE 'Expected UPDATE denial (SQLSTATE 42501)';
    END;
END;
$verify$;
ROLLBACK;
SELECT 'PASS: fixture counts, order 101 total, and UPDATE denial' AS result;
