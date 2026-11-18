"""Offline client checks and opt-in acceptance tests for the disposable lab."""

import json
import os
import unittest

from client import connect, validate_loopback_url


class ClientConfigurationTests(unittest.TestCase):
    def test_accepts_loopback_http_without_credentials(self):
        for url in (
            "http://127.0.0.1:9876/mcp",
            "http://localhost:9876/mcp",
            "http://[::1]:9876/mcp",
        ):
            with self.subTest(url=url):
                validate_loopback_url(url)

    def test_rejects_non_loopback_or_credentialed_urls(self):
        for url in (
            "https://127.0.0.1:9876/mcp",
            "http://example.test:9876/mcp",
            "http://" + "user" + ":" + "password" + "@127.0.0.1:9876/mcp",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_loopback_url(url)


def tool_text(result):
    return "\n".join(
        item.text for item in result.content if getattr(item, "type", None) == "text"
    )


def graphql_rows(result, expected_name):
    for line in tool_text(result).splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("name") == expected_name:
            response = payload.get("response")
            return json.loads(response) if isinstance(response, str) else response
    return None


def has_http_status(error, expected):
    response = getattr(error, "response", None)
    if response is not None and response.status_code in expected:
        return True
    return any(
        has_http_status(child, expected)
        for child in getattr(error, "exceptions", ())
    )


@unittest.skipUnless(os.getenv("MCP_TEST_URL"), "MCP_TEST_URL not configured")
class MCPAcceptanceTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.environ["MCP_TEST_URL"]
        validate_loopback_url(cls.url)
        cls.tokens = {
            "ADA": os.getenv("EXO_TEST_ADA_TOKEN"),
            "LIN": os.getenv("EXO_TEST_LIN_TOKEN"),
            "STAFF": os.getenv("EXO_TEST_STAFF_TOKEN"),
        }
        missing = [name for name, token in cls.tokens.items() if not token]
        if missing:
            raise ValueError(f"Missing locally signed lab tokens: {', '.join(missing)}")

    async def invoke(self, tool_name, query, token=None):
        async with connect(self.url, token) as session:
            return await session.call_tool(
                tool_name,
                arguments={"query": query},
            )

    async def test_discovery_exposes_only_read_only_allowlist(self):
        async with connect(self.url) as session:
            result = await session.list_tools()
        self.assertEqual(
            {tool.name for tool in result.tools},
            {
                "execute_query-customer_order_history",
                "execute_query-staff_sales_report",
            },
        )

    async def test_customer_order_history_and_nested_results_are_isolated(self):
        query = """
        query {
          orders {
            orderId
            customer { customerId }
            orderItems {
              orderItemId
              quantity
              unitPriceCents
              product { sku }
            }
          }
        }
        """
        for name, customer_id, order_id, line_ids, total in (
            ("ADA", 1, 101, {1001, 1002}, 3200),
            ("LIN", 2, 102, {1003}, 1200),
        ):
            with self.subTest(customer=name):
                result = await self.invoke(
                    "execute_query-customer_order_history", query, self.tokens[name]
                )
                orders = graphql_rows(result, "orders")
                self.assertFalse(result.isError, tool_text(result))
                self.assertEqual([row["orderId"] for row in orders], [order_id])
                self.assertEqual(orders[0]["customer"]["customerId"], customer_id)
                self.assertEqual(
                    {line["orderItemId"] for line in orders[0]["orderItems"]},
                    line_ids,
                )
                self.assertEqual(
                    sum(
                        line["quantity"] * line["unitPriceCents"]
                        for line in orders[0]["orderItems"]
                    ),
                    total,
                )

    async def test_malformed_sql_and_mutations_are_rejected(self):
        try:
            malformed = await self.invoke(
                "execute_query-customer_order_history", "query { orders {"
            )
        except Exception as error:
            self.assertTrue(has_http_status(error, {400}), repr(error))
        else:
            self.assertTrue(
                malformed.isError or "errors" in tool_text(malformed).lower(),
                tool_text(malformed),
            )

        rejected_queries = (
            "query { products { sku } }",
            'mutation { createCustomer(customerName: "Mallory") { customerId } }',
            "SELECT * FROM commerce.orders",
        )
        for query in rejected_queries:
            with self.subTest(query=query):
                try:
                    result = await self.invoke(
                        "execute_query-customer_order_history",
                        query,
                        self.tokens["ADA"],
                    )
                except Exception as error:
                    self.assertTrue(has_http_status(error, {400}), repr(error))
                else:
                    self.assertTrue(
                        result.isError or "errors" in tool_text(result).lower(),
                        tool_text(result),
                    )

    async def test_report_result_is_bounded_and_staff_only(self):
        query = """
        query {
          staffSalesReport(
            startDate: "2026-01-01",
            endDate: "2026-02-01",
            limit: 1
          ) { category revenueCents }
        }
        """
        result = await self.invoke(
            "execute_query-staff_sales_report", query, self.tokens["STAFF"]
        )
        rows = graphql_rows(result, "staffSalesReport")
        self.assertFalse(result.isError, tool_text(result))
        self.assertLessEqual(len(rows), 1)
        self.assertEqual(rows, [{"category": "Books", "revenueCents": 3600}])

        try:
            invalid_limit = await self.invoke(
                "execute_query-staff_sales_report",
                query.replace("limit: 1", "limit: 101"),
                self.tokens["STAFF"],
            )
        except Exception as error:
            self.assertTrue(has_http_status(error, {400}), repr(error))
        else:
            self.assertTrue(
                invalid_limit.isError
                or "error" in tool_text(invalid_limit).lower()
                or "errors" in tool_text(invalid_limit).lower(),
                tool_text(invalid_limit),
            )

        for caller in ("ADA", "LIN"):
            with self.subTest(caller=caller):
                try:
                    denied = await self.invoke(
                        "execute_query-staff_sales_report",
                        query,
                        self.tokens[caller],
                    )
                except Exception as error:
                    self.assertTrue(has_http_status(error, {401, 403}), repr(error))
                else:
                    self.assertIn(
                        graphql_rows(denied, "staffSalesReport"),
                        (None, []),
                        tool_text(denied),
                    )

    async def test_anonymous_cannot_read_customer_history(self):
        try:
            result = await self.invoke(
                "execute_query-customer_order_history",
                "query { orders { orderId } }",
            )
        except Exception as error:
            self.assertTrue(has_http_status(error, {401, 403}), repr(error))
            return
        rows = graphql_rows(result, "orders")
        self.assertIn(rows, (None, []))
        self.assertNotIn("101", tool_text(result))
        self.assertNotIn("102", tool_text(result))

    async def test_staff_cannot_read_raw_customer_orders(self):
        try:
            result = await self.invoke(
                "execute_query-staff_sales_report",
                "query { orders { orderId customer { customerId } } }",
                self.tokens["STAFF"],
            )
        except Exception as error:
            self.assertTrue(has_http_status(error, {401, 403}), repr(error))
            return
        rows = graphql_rows(result, "orders")
        self.assertIn(rows, (None, []))


if __name__ == "__main__":
    unittest.main()
