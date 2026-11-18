# Module 6 — Capstone and Operations

*Exograph with PostgreSQL: Semantic Modeling & MCP · Goliath Research Academy*

[Course plan](../README.md) · [Module 5](../5%20-%20Python%20MCP%20Client%20and%20Verification/05_content.md) · [Runbook](RUNBOOK.md)

## Capstone

From a clean checkout, run the disposable database, the pinned Exograph MCP
profiles, and the Module 5 acceptance suite by following the
[runbook](RUNBOOK.md). The deliverables are the customer order-history tool,
the staff-only category sales report, automated authorization checks, and an
independent SQL reconciliation. No production service, additional database
grant, schema migration, or LLM account is part of the exercise.

## Report contract

`staffSalesReport` returns one row per category for the half-open UTC window
`[2026-01-01, 2026-02-01)`. Only `PAID` and `SHIPPED` orders qualify. Revenue
is the sum of `quantity * unit_price_cents`, represented as integer cents.
Rows are ordered by category ascending and the caller-supplied result limit is
an integer from 1 through 100. The report contains no customer identifiers or
names.

Run [`staff_report_reconciliation.sql`](staff_report_reconciliation.sql) as
the read-only runtime user. It independently computes the same category
totals from the base tables and then checks order 101's two lines total
3,200 cents. The expected January category totals are Books: 3,600 cents and
Games: 800 cents.

## Evidence and limits

Record CLI version, fixture verification, offline test results, and live test
results separately. Live tests count only when run against the disposable
loopback lab with the signed local identities. A skipped live test is not a
pass; do not copy credentials or bearer tokens into the evidence.
