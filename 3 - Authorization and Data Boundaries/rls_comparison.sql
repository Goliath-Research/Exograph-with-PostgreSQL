\set ON_ERROR_STOP on

-- Run as the setup role (lab_admin) on the disposable Module 1 database.
-- The transaction enables row-level security, shows one policy, then rolls
-- back. commerce.orders is unchanged when this script finishes, so the
-- Exograph runtime role keeps the grants from bootstrap.sql.
--
-- lab_admin is the database superuser and bypasses row-level security.
-- The filtered reads run as exograph_runtime, which has SELECT and does not.

BEGIN;
ALTER TABLE commerce.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE commerce.orders FORCE ROW LEVEL SECURITY;
CREATE POLICY orders_own_rows ON commerce.orders
    FOR SELECT
    USING (customer_id = current_setting('app.customer_id')::integer);

SET LOCAL ROLE exograph_runtime;
SET LOCAL app.customer_id = '1';
DO $ada$
DECLARE
    visible integer[];
BEGIN
    SELECT array_agg(order_id ORDER BY order_id) INTO visible FROM commerce.orders;
    IF visible IS DISTINCT FROM ARRAY[101] THEN
        RAISE EXCEPTION 'Ada policy: expected order 101, saw %', visible;
    END IF;
END;
$ada$;

SET LOCAL app.customer_id = '2';
DO $lin$
DECLARE
    visible integer[];
BEGIN
    SELECT array_agg(order_id ORDER BY order_id) INTO visible FROM commerce.orders;
    IF visible IS DISTINCT FROM ARRAY[102] THEN
        RAISE EXCEPTION 'Lin policy: expected order 102, saw %', visible;
    END IF;
END;
$lin$;

ROLLBACK;
SELECT 'PASS: rolled back; RLS was a comparison, not the Exograph policy' AS result;
