# Module 4 — Exograph MCP Profiles

*Exograph with PostgreSQL: Semantic Modeling & MCP · Goliath Research Academy*

[Course plan](../README.md) · [Module 3](../3%20-%20Authorization%20and%20Data%20Boundaries/03_content.md) · [Module 5](../5%20-%20Python%20MCP%20Client%20and%20Verification/05_content.md)

## Goal

Run the existing Module 3 model as a loopback-only MCP server. The profiles in
[`../3 - Authorization and Data Boundaries/exo.toml`](../3%20-%20Authorization%20and%20Data%20Boundaries/exo.toml)
allow only the `orders` and `staffSalesReport` query operations. They create
two tools, `execute_query-customer_order_history` and
`execute_query-staff_sales_report`; mutations are explicitly not included.
The first tool can return order history with nested lines, while the second
returns the bounded category report. The staff profile also includes `orders`
because the report's privileged implementation queries order data internally;
the existing model policy still denies staff direct order-history reads.
Neither profile exposes arbitrary SQL.

Tool discovery is not authorization. The existing Module 3 access rules still
decide which rows a caller may read. Do not weaken, replace, or infer identity
from GraphQL arguments to make a tool call work.

## Start the server

The CLI is pinned to Exograph `0.29.1` in `exo.toml`. Use the same disposable
database, `exograph_runtime` read-only role, and locally signed synthetic
identities from Modules 1–3. Do not migrate the database or grant additional
privileges. Keep the signing secret and tokens in local shell variables; do
not save or commit real values. Use an alphanumeric throwaway runtime password
so it can be placed in the local database URL without URL-encoding ambiguity.

In PowerShell, start the database as described in the [Module 1 runbook](../1%20-%20Reproducible%20PostgreSQL%20Lab/RUNBOOK.md), then start Exograph from the model directory:

```powershell
Set-Location '3 - Authorization and Data Boundaries'
$env:EXO_SERVER_HOST = '127.0.0.1'
$env:EXO_SERVER_PORT = '9876'
$env:EXO_MCP_MODE = 'combined'
$env:EXO_POSTGRES_READ_WRITE = 'false'
$env:EXO_POSTGRES_URL = ('postgresql://' + 'exograph_runtime:' + $env:LAB_RUNTIME_PASSWORD + '@127.0.0.1:55432/exograph_commerce')
# Set EXO_JWT_SECRET locally to the key used to sign the Module 3 lab identities.
exo --version
exo build
exo dev
```

The server listens on `127.0.0.1:9876`; its MCP endpoint is
`http://127.0.0.1:9876/mcp`. Keep `EXO_MCP_MODE=combined` so each profile has
only its execute tool and no separate introspection tool. The profile's
GraphQL schema describes the permitted operation. An invalid or excluded
operation must fail; it is not permission to issue raw SQL.

## Verify separation of controls

Use the anonymous identity first to discover tools. Discovery should return
exactly the two profile tools. Then call `orders` without a token and confirm
that it returns no protected data. Repeat with Ada and Lin's existing signed
tokens: each sees only their own order and nested lines. A staff token can call
the report but must not gain customer-history access. A customer token must
not read the report.

These are different checks: a visible tool can still deny a caller, and an
authorized model query does not make an unlisted operation discoverable.
Module 5 automates both sides of that distinction.
