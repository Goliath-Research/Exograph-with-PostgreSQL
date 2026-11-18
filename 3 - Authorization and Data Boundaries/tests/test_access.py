"""Opt-in acceptance tests for the planned Exograph GraphQL contract.

Set EXO_TEST_URL to the local GraphQL URL and EXO_TEST_ADA_TOKEN,
EXO_TEST_LIN_TOKEN, EXO_TEST_STAFF_TOKEN, EXO_TEST_EXPIRED_TOKEN, and
EXO_TEST_MISSING_ID_TOKEN to signed lab tokens. Never commit tokens.
Run python -m unittest discover -s "3 - Authorization and Data Boundaries/tests" -v.
Adjust field names to the checked-in model when that model lands.
"""
import json
import os
import unittest
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


@unittest.skipUnless(os.getenv('EXO_TEST_URL'), 'Exograph endpoint not configured')
class AccessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.environ['EXO_TEST_URL']
        url = urlsplit(cls.url)
        if url.scheme not in ('http', 'https') or url.hostname not in ('127.0.0.1', '::1', 'localhost') or url.username or url.password:
            raise ValueError('Use a loopback lab URL without credentials')
        cls.tokens = {name: os.environ['EXO_TEST_' + name + '_TOKEN']
                      for name in ('ADA', 'LIN', 'STAFF', 'EXPIRED', 'MISSING_ID')}

    def query(self, document, token=None, variables=None, allow_auth_http=False):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = Request(self.url, json.dumps({'query': document, 'variables': variables or {}}).encode(), headers)
        try:
            with build_opener(NoRedirect()).open(request, timeout=5) as response:
                return json.load(response)
        except HTTPError as exc:
            if allow_auth_http and exc.code in (401, 403):
                return {'data': None}
            raise

    def orders(self, token):
        result = self.query('{ orders { orderId orderItems { orderItemId } } }', token)
        self.assertFalse(result.get('errors'), 'Order list failed')
        return result['data']['orders']

    def test_unfiltered_lists_and_nested_lines(self):
        for name, order, lines in (('ADA', 101, [1001, 1002]), ('LIN', 102, [1003])):
            with self.subTest(caller=name):
                rows = self.orders(self.tokens[name])
                self.assertEqual([row['orderId'] for row in rows], [order])
                self.assertEqual(sorted(item['orderItemId'] for item in rows[0]['orderItems']), lines)

    def test_direct_lookup_uses_verified_owner(self):
        document = 'query($id: Int!) { order(orderId: $id) { orderId } }'
        for name, own, other in (('ADA', 101, 102), ('LIN', 102, 101)):
            with self.subTest(caller=name):
                token = self.tokens[name]
                positive = self.query(document, token, {'id': own})
                self.assertFalse(positive.get('errors'), 'Own order lookup failed')
                self.assertEqual(positive['data']['order']['orderId'], own)
                denied = self.query(document, token, {'id': other}, allow_auth_http=True)
                self.assertIsNone((denied.get('data') or {}).get('order'))

    def test_untrusted_identities_get_no_orders(self):
        self.orders(self.tokens['ADA'])
        document = '{ orders { orderId orderItems { orderItemId } } }'
        for name, token in [('ANONYMOUS', None), ('INVALID', 'invalid.token.signature')] + [
            (key, self.tokens[key]) for key in ('STAFF', 'EXPIRED', 'MISSING_ID')
        ]:
            with self.subTest(caller=name):
                result = self.query(document, token, allow_auth_http=True)
                self.assertIn((result.get('data') or {}).get('orders'), (None, []))
