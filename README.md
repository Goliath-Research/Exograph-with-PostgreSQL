# *Relational Databases with Python*
# Exograph with PostgreSQL: Semantic Modeling & MCP

*Relational Databases with Python · Course 3 · Goliath Research Academy*

Build a semantic layer over an existing PostgreSQL database and expose a
read-only subset of it through the Model Context Protocol (MCP). Use Exograph
to define the domain model and access rules, then use Python to discover,
call, and test the resulting MCP tools.

> **Status:** Guides and lab artifacts for Modules 1–6 are implemented. The
> course owner has locally verified Modules 1–3. This implementation built
> with Exograph 0.29.1, passed the Module 5 live MCP suite against a disposable
> loopback lab, and reconciled Module 6's SQL totals. A separate clean-checkout
> rehearsal is not claimed.

## Prerequisites

Complete [PostgreSQL with Python: Advanced Relational Databases](https://github.com/Goliath-Research/PostgreSQL-with-Python)
or have equivalent experience with SQL, PostgreSQL roles and privileges, and
basic Python testing. Familiarity with Docker Compose is helpful. No prior
Exograph or MCP experience is assumed.

## What you'll build

The course continues the e-commerce project from PostgreSQL with Python.
You'll work with synthetic customers, orders, order lines, and products in a
disposable PostgreSQL database. The course does not require access to a live
store, production credentials, or an LLM account.

    Python MCP client and tests
               |
               v
    Exograph MCP interface
               |
               v
    Domain model and access rules
               |
               v
    PostgreSQL commerce schema

PostgreSQL remains the system of record. The Exograph model describes what
the data means, how entities relate, and who may access them. MCP exposes
selected operations to clients. Python is used for the client and tests;
it does not run a second MCP server.

## Learning outcomes

By the end of the course, you'll be able to:

- Import an existing PostgreSQL schema and refine it into a domain model.
- Define relationships, report grain, status eligibility, and money units
  so that clients can interpret results correctly.
- Distinguish PostgreSQL privileges, model authorization, and MCP tool exposure.
- Connect a Python MCP client, discover available tools, and validate results.
- Test that customers cannot read one another's data, including through
  nested relationships, and that staff access stays within its intended scope.
- Reconcile a bounded report against an independent SQL query and document
  how to reproduce the result.

## Six-module lesson plan

| Module | Lab | Guide status | Evidence of completion |
| :--- | :--- | :--- | :--- |
| [1. Reproducible PostgreSQL Lab](1%20-%20Reproducible%20PostgreSQL%20Lab/01_content.md) | Start a disposable database, load a deterministic `commerce` fixture, and separate setup credentials from the restricted runtime role. | Implemented · locally verified by course owner | Verify fixture row counts, approved reads, and denied writes. |
| [2. Import and Refine the Exograph Model](2%20-%20Import%20and%20Refine%20the%20Exograph%20Model/02_content.md) | Import the schema, review the generated model, and map customers, orders, order lines, and products. Document identifiers, relationships, historical prices, and report grain. | Implemented · locally verified by course owner | Match an order and its lines to a hand-checked SQL result. |
| [3. Authorization and Data Boundaries](3%20-%20Authorization%20and%20Data%20Boundaries/03_content.md) | Define rules for anonymous callers, two synthetic customers, and a staff user. Base access decisions on verified identity claims, not tool arguments. | Implemented · locally verified by course owner | Show that each customer can retrieve their own orders but not another customer's orders, directly or through a relationship. |
| [4. Exograph MCP Profiles](4%20-%20Exograph%20MCP%20Profiles/04_content.md) | Expose selected read-only operations through Exograph's MCP interface. Compare tool visibility with data authorization. | Implemented · CLI build and local MCP checks passed | Verify discovery lists only intended tools, and neither arbitrary SQL nor mutations are exposed. |
| [5. Python MCP Client and Verification](5%20-%20Python%20MCP%20Client%20and%20Verification/05_content.md) | Connect a Python client and test discovery, successful calls, invalid inputs, bounded results, and access denials. | Implemented · live acceptance suite passed on disposable lab | Run protocol tests with deterministic fixtures and no LLM account. |
| [6. Capstone and Operations](6%20-%20Capstone%20and%20Operations/06_content.md) | Deliver customer order history and a bounded staff sales report. Reconcile the report, audit access, and write a reproducible runbook. | Implemented · SQL reconciliation passed; clean-checkout rehearsal not run | Demonstrate the capstone from a clean setup, with passing authorization tests and matching SQL totals. |

## Capstone: Customer order history and staff sales reporting

Build two read-only capabilities over the same database:

1. **Customer order history.** An authenticated customer can retrieve their own
   orders and line items. A caller cannot obtain another customer's data by
   changing an identifier, using an alternate query, or traversing a relationship.
2. **Staff sales reporting.** An authorized staff caller can retrieve a bounded
   category sales report. Document the date range, included order statuses,
   result limit, money unit, and how totals are calculated. Reconcile the output
   against SQL on the same fixture.

Submit the Exograph model and MCP profile, the database fixture and grants,
the Python client and tests, a reconciliation query, and a runbook that
another learner can follow from a clean checkout.

| Assessment | Weight |
| :--- | ---: |
| Reproducible database lab and clear domain model | 25% |
| Authorization rules and cross-customer isolation tests | 30% |
| MCP tool contract, Python client, and protocol tests | 25% |
| Report accuracy, reconciliation, and operational runbook | 20% |

A correct report does not compensate for a data leak. Any unauthorized
cross-customer read must be fixed before the capstone passes.

## Lab boundaries

- Use synthetic data and a disposable database. Bind local lab services to
  loopback and keep credentials outside version control.
- Keep the first implementation read-only. Public hosting, write tools,
  and production identity-provider integration are outside the core course.
- Treat tool discovery, model authorization, and database privileges as
  separate controls. Test each one independently.
- The verified setup guide will identify the supported Exograph, PostgreSQL,
  and Python versions and include startup and test commands.

## Course series

1. [SQLite with Python: Relational Database Foundations](https://github.com/Goliath-Research/SQLite-with-Python)
2. [PostgreSQL with Python: Advanced Relational Databases](https://github.com/Goliath-Research/PostgreSQL-with-Python)
3. **Exograph with PostgreSQL: Semantic Modeling & MCP** — this repository

See [LICENSE](LICENSE) for repository licensing.
