#!/usr/bin/env python

import unittest
from dns_forward_server_verbose import Logger
from collections import namedtuple

DNSPayload = namedtuple('DNSPayload', 'AQuery, AResponse, AServerFailure, '
                                      'ANXDomain, AAAAQuery, AAAAResponse, '
                                      'AAAAServerFailure, AAAANXDomain')


def log_print(label, message):
    print("%s: %s" % (label,  message))


def log_title(message):
    log_print('CASE', message)


def log_desc(message):
    log_print('DESC', message)


def log_debug(message):
    log_print('DEBUG', message)


class DPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = Logger()
        cls.target = DNSPayload(
            '\x00\x02\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77'
            '\x06\x67\x6F\x6F\x67\x6C\x65\x03\x63\x6F\x6D\x02\x74\x77\x00\x00'
            '\x01\x00\x01',
            '\x00\x02\x81\x80\x00\x01\x00\x10\x00\x00\x00\x00\x03\x77\x77\x77'
            '\x06\x67\x6F\x6F\x67\x6C\x65\x03\x63\x6F\x6D\x02\x74\x77\x00\x00'
            '\x01\x00\x01\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\x98\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\x99\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xA2\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\x9E\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xA8\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xA3\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xBB\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xAD\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xA7\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\x94\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xB2\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xB1\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xB7\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\x9D\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xB6\xC0\x0C\x00\x01\x00\x01\x00\x00\x01\x2B\x00\x04\xD2'
            '\x3D\xDD\xAC',
            '\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x2E\x6E\x6F\x74'
            '\x2E\x66\x6F\x75\x6E\x64\x2E\x74\x61\x69\x70\x65\x69\x2E\x2E\x2E'
            '\x2E\x2E',
            '\x00\x04\x81\x83\x00\x01\x00\x00\x00\x01\x00\x00\x01\x31\x01\x32'
            '\x01\x33\x01\x34\x01\x35\x06\x67\x6F\x6F\x67\x6C\x65\x03\x63\x6F'
            '\x6D\x00\x00\x01\x00\x01\xC0\x16\x00\x06\x00\x01\x00\x00\x00\x3B'
            '\x00\x26\x03\x6E\x73\x33\xC0\x16\x09\x64\x6E\x73\x2D\x61\x64\x6D'
            '\x69\x6E\xC0\x16\x06\x9F\xA7\x72\x00\x00\x03\x84\x00\x00\x03\x84'
            '\x00\x00\x07\x08\x00\x00\x00\x3C',
            '\x00\x03\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77'
            '\x06\x67\x6F\x6F\x67\x6C\x65\x03\x63\x6F\x6D\x02\x74\x77\x00\x00'
            '\x1C\x00\x01',
            '\x00\x03\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03\x77\x77\x77'
            '\x06\x67\x6F\x6F\x67\x6C\x65\x03\x63\x6F\x6D\x02\x74\x77\x00\x00'
            '\x1C\x00\x01\xC0\x0C\x00\x1C\x00\x01\x00\x00\x01\x2B\x00\x10\x24'
            '\x04\x68\x00\x40\x02\x08\x03\x00\x00\x00\x00\x00\x00\x10\x1F',
            '\x00\x03\x81\x82\x00\x01\x00\x00\x00\x00\x00\x00\x03\x6E\x6F\x74'
            '\x05\x66\x6F\x75\x6E\x64\x06\x74\x61\x69\x70\x65\x69\x00\x00\x1C'
            '\x00\x01',
            '\x00\x05\x81\x83\x00\x01\x00\x00\x00\x01\x00\x00\x01\x31\x01\x32'
            '\x01\x33\x01\x34\x01\x35\x06\x67\x6F\x6F\x67\x6C\x65\x03\x63\x6F'
            '\x6D\x00\x00\x1C\x00\x01\xC0\x16\x00\x06\x00\x01\x00\x00\x02\x57'
            '\x00\x26\x03\x6E\x73\x34\xC0\x16\x09\x64\x6E\x73\x2D\x61\x64\x6D'
            '\x69\x6E\xC0\x16\x06\x9F\xA7\x72\x00\x00\x03\x84\x00\x00\x03\x84'
            '\x00\x00\x07\x08\x00\x00\x00\x3C'
        )

    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)

    def testAQuery(self):
        log_desc('Type A Query for google')
        result = self.logger.dpiengine('dns', self.target.AQuery)
        # log_debug(result)
        self.assertEqual(1, len(result))
        self.assertTrue('www.google.com.tw' in result[0])

    def testAResponse(self):
        log_desc('Type A Response for google, multiple RR')
        result = self.logger.dpiengine('dns', self.target.AResponse)
        # log_debug(result)
        self.assertGreaterEqual(len(result), 3)
        self.assertIn('A{210.61.221.153}', result)
        self.assertIn('A{210.61.221.182}', result)
        self.assertIn('A{210.61.221.173}', result)

    def testAServerFailure(self):
        log_desc('Type A Server Failure')
        result = self.logger.dpiengine('dns', self.target.AServerFailure)
        log_desc('there should be no answer returned')
        self.assertEqual(0, len(result))

    def testANXDomain(self):
        log_desc('Type A No Such Domain')
        result = self.logger.dpiengine('dns', self.target.ANXDomain)
        log_desc('there should be NXDomain returned')
        self.assertEqual(1, len(result))
        if len(result) > 0:
            self.assertIn('nxdomain', result[0].lower())

    def testAAAAQuery(self):
        log_desc('Type AAAA Query')
        result = self.logger.dpiengine('dns', self.target.AAAAQuery)
        # log_debug(result)
        self.assertEqual(1, len(result))
        self.assertTrue('AAAA' in result[0])
        self.assertTrue('www.google.com.tw' in result[0])

    def testAAAAResponse(self):
        log_desc('Type AAAA Response')
        result = self.logger.dpiengine('dns', self.target.AAAAResponse)
        # log_debug(result)
        self.assertEqual(len(result), 1)
        self.assertIn('AAAA{2404:6800:4002:803::101f}', result)

    def testAAAAServerFailure(self):
        log_desc('Type AAAA Server Failure')
        result = self.logger.dpiengine('dns', self.target.AAAAServerFailure)
        # log_debug(result)
        log_desc('there should be no answer returned')
        self.assertEqual(0, len(result))

    def testAAAANXDomain(self):
        log_desc('Type AAAA No Such Domain')
        result = self.logger.dpiengine('dns', self.target.AAAANXDomain)
        # log_debug(result)
        log_desc('there should be no answer returned')
        # self.assertEqual(1, len(result))
        # self.assertTrue('www.google.com.tw' in result[0])

    def testWorryFreeAPI(self):
        log_desc('dnslib.DNSError from AAAA Server Failure was caught withing '
                 'dpiengine_worry_free ')
        result = self.logger.dpiengine_worry_free('dns',
                                                  self.target.AAAAServerFailure)
        log_desc('there should be no answer returned and no exception observed')
        self.assertEqual(0, len(result))


if __name__ == '__main__':
    unittest.main()
