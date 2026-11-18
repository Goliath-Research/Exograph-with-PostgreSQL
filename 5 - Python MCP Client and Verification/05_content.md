# Module 5 — Python MCP Client and Verification

*Exograph with PostgreSQL: Semantic Modeling & MCP · Goliath Research Academy*

[Course plan](../README.md) · [Module 4](../4%20-%20Exograph%20MCP%20Profiles/04_content.md) · [Module 6](../6%20-%20Capstone%20and%20Operations/06_content.md)

## Goal

Use the pinned Python MCP SDK `1.28.1` to discover and invoke Exograph's two
profile tools. The client negotiates protocol version `2025-06-18`, supported
by the pinned Exograph CLI, rather than advertising a newer protocol. The test
client talks directly to the Streamable HTTP MCP endpoint; it
does not call an LLM or run a second MCP server. The live acceptance tests use
the signed synthetic tokens already used by Module 3.

## Install and test

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r '5 - Python MCP Client and Verification/requirements.txt'
python -m unittest discover -s '5 - Python MCP Client and Verification/tests' -t '5 - Python MCP Client and Verification' -v
```

The default test run is offline and checks that the client rejects non-loopback
URLs. Live protocol tests are opt-in. Start the Module 1 database and Module 4
server, then set the existing locally generated Module 3 tokens in the shell:

```powershell
$env:MCP_TEST_URL = 'http://127.0.0.1:9876/mcp'
$env:EXO_TEST_ADA_TOKEN = '<local signed Ada token>'
$env:EXO_TEST_LIN_TOKEN = '<local signed Lin token>'
$env:EXO_TEST_STAFF_TOKEN = '<local signed staff token>'
python -m unittest discover -s '5 - Python MCP Client and Verification/tests' -t '5 - Python MCP Client and Verification' -v
```

The endpoint validator permits only HTTP loopback URLs without embedded
credentials. Never set the live-test variables to production credentials.
Without `MCP_TEST_URL`, protocol tests are reported as skipped rather than
passed.

## Acceptance checks

The live tests cover:

- exact MCP tool discovery, independent of caller authentication;
- a successful customer order-history call and nested line data;
- malformed GraphQL and a query excluded by the profile;
- a staff report bounded to the requested result limit and rejection of an
  out-of-range limit;
- anonymous denial, customer-to-customer isolation in orders and nested
  results, and staff access limited to the approved report.

For each denial, an MCP error or an empty/null protected result is acceptable;
any other customer's order or line identifiers in the response are not.
Discovery alone is not proof of access control.
