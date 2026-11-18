# Module 1 — Reproducible PostgreSQL Lab

*Exograph with PostgreSQL: Semantic Modeling & MCP · Goliath Research Academy*

Return to the [course plan](../README.md).

This lab includes [Compose configuration](compose.yaml), [bootstrap SQL](bootstrap.sql), [automated SQL verification](verify.sql), and a step-by-step [Runbook](RUNBOOK.md).

## Goal

Prepare the disposable PostgreSQL database that Module 2 will import into Exograph. Use synthetic e-commerce data and prove that the runtime role can query the intended tables without being able to change them.

## Lab sequence

1. Start a fresh PostgreSQL instance and bind any published database port to loopback. Keep credentials outside version control and do not point the lab at a production or shared database.
2. As the setup role, create the `commerce` schema and load a deterministic fixture with two customers, products, and orders with line items. Give each customer at least one order. Record the fixture's expected row counts and one hand-calculated order total in integer cents, using the charged price on each line.
3. Provision a separate runtime login that does not own the schema or tables. Grant schema `USAGE` and `SELECT` only on the intended relations. Keep setup credentials out of the Exograph runtime configuration.
4. Reconnect as the runtime login and verify the database and identity with `SELECT current_database(), current_user;`. Check the recorded row counts and order total. Verify that an `UPDATE` on a disposable fixture row is denied; run this check in its own transaction and roll back even if it unexpectedly succeeds. Do not count a connection error or a missing table as a successful denial.
5. Rebuild from a fresh disposable database and repeat the checks. Record the PostgreSQL version and the commands you actually used.

## Evidence to submit

- Expected versus observed row counts for customers, products, orders, and order lines.
- One reconciled order total, with the unit and calculation shown.
- The runtime identity, evidence of an approved read, and the expected permission-denied result for a write. Omit passwords and connection strings.

## Handoff to Module 2

Carry forward the schema, fixture, and verification results. The runtime role limits what the Exograph service can do in PostgreSQL; it does not by itself isolate customers from one another. Later modules add and test that policy in the Exograph model.
