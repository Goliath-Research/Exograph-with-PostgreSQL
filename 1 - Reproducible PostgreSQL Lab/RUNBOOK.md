# Run and verify Module 1

Use Docker Compose and PowerShell. This lab is disposable and does not use the PostgreSQL database from the previous course. Run from the repository root:

```powershell
Set-Location '1 - Reproducible PostgreSQL Lab'
```

Set distinct local values for `LAB_ADMIN_PASSWORD` and `LAB_RUNTIME_PASSWORD` in your shell or an untracked `.env` in this directory. Do not commit the values. Optionally set `LAB_POSTGRES_PORT` if host port 55432 is occupied. A host port override does not change the container port used below.

```powershell
docker compose up -d --wait
docker compose ps
```

If startup fails, inspect `docker compose logs postgres` locally. The bootstrap runs only when PostgreSQL initializes an empty data volume. For a fresh-run rehearsal, `docker compose down --volumes` deletes this project's lab database; use it only when you intend to discard the fixture and all local changes, then rerun startup.

Run the automated SQL checks over TCP as the restricted login. Enter the runtime password at the prompt:

```powershell
docker compose cp verify.sql postgres:/tmp/module1-verify.sql
docker compose exec postgres psql -X -h 127.0.0.1 -U exograph_runtime -d exograph_commerce -W -v ON_ERROR_STOP=1 -f /tmp/module1-verify.sql
```

Expect `Expected UPDATE denial (SQLSTATE 42501)` and a final `PASS` row. The checks assert 2 customers, 2 products, 2 orders, 3 lines, and 3,200 cents for order 101. The write probe runs in a transaction; an unexpectedly successful UPDATE fails the check and is not committed. A connection failure or missing table is not a pass.

Use `docker compose stop` to stop the lab without deleting data. For Module 2, keep the working database and connect as `exograph_runtime` through the published loopback port. Do not use administrator credentials for schema import.
