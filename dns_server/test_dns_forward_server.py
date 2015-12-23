#!/usr/bin/env python

import unittest
from dns_forward_server import *


def log_print(label, message):
    print("%s: %s" % (label,  message))


def log_title(message):
    log_print('CASE', message)


def log_desc(message):
    log_print('DESC', message)


def log_debug(message):
    log_print('DEBUG', message)


class UtilityTest(unittest.TestCase):

    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)

    def testNothing(self):
        log_desc('no parameters specified')
        self.assertEqual(parse_parameter([]), (None, None, None))

    def testExample(self):
        testdata = '-p 10053 -f 8.8.8.8:53'
        log_desc(testdata)
        self.assertEqual(parse_parameter(testdata.split()),
                         (10053, '8.8.8.8', 53))

    def testPrivateIP(self):
        testdata = '-p 10053 -f 192.168.1.1:53'
        log_desc(testdata)
        self.assertEqual(parse_parameter(testdata.split()),
                         (10053, '192.168.1.1', 53))

    def testUserError(self):
        testdata = '-p 10053 -f 192.168.1.153'
        log_desc(testdata)
        self.assertEqual(parse_parameter(testdata.split()),
                         (10053, None, None))
        testdata = '-p 99999 -f 192.168.1.1:53'
        log_desc(testdata)
        self.assertEqual(parse_parameter(testdata.split()),
                         (None, '192.168.1.1', 53))

    def testNotSupportIPv6(self):
        testdata = '-p 10053 -f fe80::a838:bed2:7ef8:5950:53'
        log_desc(testdata)
        self.assertEqual(parse_parameter(testdata.split()),
                         (10053, None, None))

    def testNotSupportDomainName(self):
        testdata = '-p 10053 -f google-public-dns-a.google.com:53'
        log_desc(testdata)
        self.assertEqual(parse_parameter(testdata.split()),
                         (10053, None, None))


class DNSServerTest(unittest.TestCase):
    @classmethod
    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def testCase1(self):
        pass


if __name__ == '__main__':
    unittest.main()
