# Module 2 — Import and Refine the Exograph Model

*Exograph with PostgreSQL: Semantic Modeling & MCP · Goliath Research Academy*

[Course plan](../README.md) · [Module 1](../1%20-%20Reproducible%20PostgreSQL%20Lab/01_content.md)

> Includes the refined baseline Exograph model ([baseline/src/index.exo](baseline/src/index.exo)) verified with Exograph CLI `0.29.1` (`exo build` and `exo schema verify`).

## Goal

Turn the Module 1 database schema into a domain model that explains relationships, identifiers, and the meaning of reported values. Treat generated code as a draft, not as a public API or authorization policy.

## Lab sequence

1. Start the disposable Module 1 database and verify the fixture as `exograph_runtime`. Record the Exograph CLI version and review `exo schema import --help` before importing the `commerce` schema. Use the restricted runtime credentials and keep connection strings out of version control and lab evidence. Import into a scratch project and review the resulting model; do not run schema-changing commands against the fixture.
2. Map `customers`, `orders`, `order_items`, and `products`. Verify the keys and relationships against the bootstrap: a customer has many orders, an order has many lines, and a line references a product by SKU. `order_item_id` identifies a line; `(order_id, line_no)` is unique within the order and determines line display order.
3. Document that `ordered_at` is a timestamp with time zone and that `unit_price_cents` is the historical charged price, not a current catalog price. An order total is the sum of quantity times charged unit price. State the grain of each result: one row per line or one row per order. Keep status filtering explicit and separate from the total calculation.
4. Compare the imported model with the hand-checked order below. Keep any local service unexposed until access rules have been added and tested in Module 3. A successful import or build does not demonstrate customer isolation.

## Reconciliation

```sql
SELECT order_id, COUNT(*) AS line_count,
       SUM(quantity::bigint * unit_price_cents) AS total_cents
FROM commerce.order_items
WHERE order_id = 101
GROUP BY order_id;
```

Expect two lines and 3,200 cents (`2 × 1,200 + 1 × 800`). Check that the model links order 101 to customer 1 and that the lines reference `BOOK-01` and `GAME-01`.

## Evidence to submit

- The imported and reviewed model, with a short description of any changes.
- The order 101 reconciliation and an explanation of line versus order grain.
- A list of fields and relationships to review for exposure in Module 3, including direct and nested paths to another customer's orders.
