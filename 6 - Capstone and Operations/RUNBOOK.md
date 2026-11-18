# Clean-checkout capstone runbook

Run these steps from the repository root in PowerShell. Use a disposable
database and local synthetic identities only. Prerequisites are Docker Compose,
Python 3.12 or newer, and Exograph CLI `0.29.1` installed from the
[pinned release](https://github.com/exograph/exograph/releases/tag/v0.29.1).

## 1. Start and verify the database

Set distinct throwaway admin and runtime passwords in the shell. Use
alphanumeric values so the runtime password can be placed in a connection URL
without URL escaping. Start PostgreSQL and run the existing Module 1
verification as documented in its [runbook](../1%20-%20Reproducible%20PostgreSQL%20Lab/RUNBOOK.md):

```powershell
Set-Location '1 - Reproducible PostgreSQL Lab'
$env:LAB_ADMIN_PASSWORD = '<local throwaway admin password>'
$env:LAB_RUNTIME_PASSWORD = '<local throwaway runtime password>'
docker compose up -d --wait
docker compose cp verify.sql postgres:/tmp/module1-verify.sql
docker compose exec postgres psql -X -h 127.0.0.1 -U exograph_runtime -d exograph_commerce -W -v ON_ERROR_STOP=1 -f /tmp/module1-verify.sql
Set-Location ..
```

The bootstrap creates a read-only runtime role. Do not rerun bootstrap,
change grants, run migrations, or use the administrator URL in Exograph.

## 2. Build and start the MCP server

Set the JWT secret to the same local-only key used to sign the Module 3 Ada,
Lin, and staff tokens. Set no production credentials. Start the server from
the Module 3 model directory:

```powershell
Set-Location '3 - Authorization and Data Boundaries'
$env:EXO_SERVER_HOST = '127.0.0.1'
$env:EXO_SERVER_PORT = '9876'
$env:EXO_MCP_MODE = 'combined'
$env:EXO_POSTGRES_READ_WRITE = 'false'
$env:EXO_POSTGRES_URL = ('postgresql://' + 'exograph_runtime:' + $env:LAB_RUNTIME_PASSWORD + '@127.0.0.1:55432/exograph_commerce')
$env:EXO_JWT_SECRET = '<local lab signing secret>'
exo --version
exo build
exo dev
```

The CLI must report `0.29.1`. The MCP server must bind to
`127.0.0.1:9876`, with endpoint `http://127.0.0.1:9876/mcp`. Keep this process
running in its terminal.

## 3. Run offline and live tests

In a second PowerShell terminal from the repository root, install the pinned
client package once and run the offline suite:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r '5 - Python MCP Client and Verification/requirements.txt'
python -m unittest discover -s '5 - Python MCP Client and Verification/tests' -t '5 - Python MCP Client and Verification' -v
```

For live protocol acceptance, provide the locally signed tokens already used
by the Module 3 tests. Do not write them to a tracked file:

```powershell
$env:MCP_TEST_URL = 'http://127.0.0.1:9876/mcp'
$env:EXO_TEST_ADA_TOKEN = '<local signed Ada token>'
$env:EXO_TEST_LIN_TOKEN = '<local signed Lin token>'
$env:EXO_TEST_STAFF_TOKEN = '<local signed staff token>'
python -m unittest discover -s '5 - Python MCP Client and Verification/tests' -t '5 - Python MCP Client and Verification' -v
```

The suite checks tool allowlisting, malformed/excluded input, result bounds,
anonymous denial, customer isolation through nested lines, and staff scope.
Without the endpoint variable, the live tests skip and provide no live
verification evidence.

## 4. Independently reconcile the report

Run the checked-in query as `exograph_runtime` from the Module 1 project
directory:

```powershell
Set-Location '1 - Reproducible PostgreSQL Lab'
docker compose cp '..\6 - Capstone and Operations\staff_report_reconciliation.sql' postgres:/tmp/staff-report-reconciliation.sql
docker compose exec postgres psql -X -h 127.0.0.1 -U exograph_runtime -d exograph_commerce -W -v ON_ERROR_STOP=1 -f /tmp/staff-report-reconciliation.sql
```

Compare January's Books total of 3,600 cents and Games total of 800 cents to
the staff tool result. The order-level check must return order 101, two lines,
and 3,200 integer cents. The SQL uses the same `[start, end)` UTC window,
`PAID`/`SHIPPED` statuses, ascending category order, and a 10-category limit.

When finished, stop the server with `Ctrl+C`, then run `docker compose down`
from the Module 1 directory. Use `docker compose down --volumes` only when you
intend to discard the disposable database.
