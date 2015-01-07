import unittest

from tests import base
from tests._testutils import run_until_complete


class TestNextset(base.AIOPyMySQLTestCase):

    def setUp(self):
        super(TestNextset, self).setUp()
        self.con = self.connections[0]

    @run_until_complete
    def test_nextset(self):
        cur = self.con.cursor()
        yield from cur.execute("SELECT 1; SELECT 2;")
        self.assertEqual([(1,)], list(cur))

        r = yield from cur.nextset()
        self.assertTrue(r)

        self.assertEqual([(2,)], list(cur))
        res = yield from cur.nextset()
        self.assertIsNone(res)

    @run_until_complete
    def test_skip_nextset(self):
        cur = self.con.cursor()
        yield from cur.execute("SELECT 1; SELECT 2;")
        self.assertEqual([(1,)], list(cur))

        yield from cur.execute("SELECT 42")
        self.assertEqual([(42,)], list(cur))

    @run_until_complete
    def test_ok_and_next(self):
        cur = self.con.cursor()
        yield from cur.execute("SELECT 1; commit; SELECT 2;")
        self.assertEqual([(1,)], list(cur))
        res = yield from cur.nextset()
        self.assertTrue(res)
        res = yield from cur.nextset()
        self.assertTrue(res)
        self.assertEqual([(2,)], list(cur))
        res = yield from cur.nextset()
        self.assertIsNone(res)

    @unittest.expectedFailure
    @run_until_complete
    def test_multi_cursor(self):
        cur1 = self.con.cursor()
        cur2 = self.con.cursor()

        yield from cur1.execute("SELECT 1; SELECT 2;")
        yield from cur2.execute("SELECT 42")

        self.assertEqual([(1,)], list(cur1))
        self.assertEqual([(42,)], list(cur2))

        res = yield from cur1.nextset()
        self.assertTrue(res)

        self.assertEqual([(2,)], list(cur1))
        res = yield from cur1.nextset()
        self.assertIsNone(res)

    #TODO: How about SSCursor and nextset?
    # It's very hard to implement correctly...
