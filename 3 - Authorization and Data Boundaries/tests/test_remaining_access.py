"""Opt-in checks for the Module 3 GraphQL contract.

Field names and argument types match the runnable Exograph model.
The staff aggregate is staffSalesReport in src/index.exo.
"""
import unittest

import test_access


@unittest.skipIf(test_access.AccessTests.__unittest_skip__ if hasattr(test_access.AccessTests, '__unittest_skip__') else False, 'Exograph endpoint not configured')
class RemainingAccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_access.AccessTests.setUpClass.__func__(cls)

    query = test_access.AccessTests.query

    def test_product_reverse_path_filters_by_owner(self):
        document = 'query($sku: String!) { product(sku: $sku) { sku orderItems { orderItemId } } }'
        for caller, expected in (('ADA', [1001]), ('LIN', [1003])):
            with self.subTest(caller=caller):
                result = self.query(document, self.tokens[caller], {'sku': 'BOOK-01'})
                self.assertFalse(result.get('errors'), 'Shared product lookup failed')
                product = result['data']['product']
                self.assertEqual(product['sku'], 'BOOK-01')
                self.assertEqual(sorted(line['orderItemId'] for line in product['orderItems']), expected)

    def test_direct_line_lookup_filters_by_owner(self):
        document = 'query($id: Int!) { orderItem(orderItemId: $id) { orderItemId } }'
        for caller, own, other in (('ADA', 1001, 1003), ('LIN', 1003, 1001)):
            with self.subTest(caller=caller):
                token = self.tokens[caller]
                positive = self.query(document, token, {'id': own})
                self.assertFalse(positive.get('errors'), 'Own line lookup failed')
                self.assertEqual(positive['data']['orderItem']['orderItemId'], own)
                denied = self.query(document, token, {'id': other}, allow_auth_http=True)
                self.assertIsNone((denied.get('data') or {}).get('orderItem'))

    def test_staff_report_reconciles_and_is_not_available_to_customers(self):
        document = '{ staffSalesReport(startDate: "2026-01-01", endDate: "2026-02-01", limit: 10) { category revenueCents } }'
        positive = self.query(document, self.tokens['STAFF'])
        self.assertFalse(positive.get('errors'), 'Staff report failed')
        rows = positive['data']['staffSalesReport']
        self.assertCountEqual(rows, [{'category': 'Books', 'revenueCents': 3600},
                                     {'category': 'Games', 'revenueCents': 800}])
        for caller in ('ADA', 'LIN', 'ANONYMOUS'):
            with self.subTest(caller=caller):
                denied = self.query(document, self.tokens.get(caller), allow_auth_http=True)
                self.assertIn((denied.get('data') or {}).get('staffSalesReport'), (None, []))
