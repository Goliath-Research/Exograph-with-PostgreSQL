\set ON_ERROR_STOP on
\getenv runtime_password LAB_RUNTIME_PASSWORD

BEGIN;
CREATE ROLE exograph_runtime LOGIN PASSWORD :'runtime_password'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
REVOKE ALL ON DATABASE exograph_commerce FROM PUBLIC;
GRANT CONNECT ON DATABASE exograph_commerce TO exograph_runtime;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

CREATE SCHEMA commerce;
REVOKE ALL ON SCHEMA commerce FROM PUBLIC;

CREATE TABLE commerce.customers (
    customer_id integer PRIMARY KEY,
    customer_name text NOT NULL
);
CREATE TABLE commerce.products (
    sku text PRIMARY KEY,
    product_name text NOT NULL,
    category text NOT NULL
);
CREATE TABLE commerce.orders (
    order_id integer PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES commerce.customers (customer_id),
    ordered_at timestamptz NOT NULL,
    order_status text NOT NULL CHECK (order_status IN ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED'))
);
CREATE TABLE commerce.order_items (
    order_item_id integer PRIMARY KEY,
    order_id integer NOT NULL REFERENCES commerce.orders (order_id),
    line_no integer NOT NULL CHECK (line_no > 0),
    sku text NOT NULL REFERENCES commerce.products (sku),
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price_cents integer NOT NULL CHECK (unit_price_cents >= 0),
    CONSTRAINT unique_constraint_order_item_order_line UNIQUE (line_no, order_id)
);

INSERT INTO commerce.customers VALUES (1, 'Ada'), (2, 'Lin');
INSERT INTO commerce.products VALUES
    ('BOOK-01', 'Database Notebook', 'Books'),
    ('GAME-01', 'Query Puzzle', 'Games');
INSERT INTO commerce.orders VALUES
    (101, 1, '2026-01-10T15:00:00Z', 'PAID'),
    (102, 2, '2026-01-11T15:00:00Z', 'SHIPPED');
INSERT INTO commerce.order_items VALUES
    (1001, 101, 1, 'BOOK-01', 2, 1200),
    (1002, 101, 2, 'GAME-01', 1, 800),
    (1003, 102, 1, 'BOOK-01', 1, 1200);

GRANT USAGE ON SCHEMA commerce TO exograph_runtime;
GRANT SELECT ON commerce.customers, commerce.products, commerce.orders,
    commerce.order_items TO exograph_runtime;
ALTER ROLE exograph_runtime IN DATABASE exograph_commerce SET search_path = commerce;
COMMIT;
