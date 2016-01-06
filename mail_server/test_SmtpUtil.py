#!/usr/bin/env python

import unittest
from SmtpUtil import SMTPUtil, RFC_NewLine


def log_print(label, message):
    print("%s: %s" % (label,  message))


def log_title(message):
    log_print('CASE', message)


def log_desc(message):
    log_print('DESC', message)


def log_debug(message):
    log_print('DEBUG', message)


class SMTPUtilTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.smtpu = SMTPUtil()
        cls.from_client_channel = None
        cls.to_client_channel = None

    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)
        self.from_client_channel = ["line1" + RFC_NewLine,
                                    "..line2" + RFC_NewLine,
                                    "...line3" + RFC_NewLine,
                                    "line end" + RFC_NewLine,
                                    "." + RFC_NewLine]
        self.to_client_channel = list()
        self.smtpu._reset()  # this is VERY important
        # if we want to reuse smtpu operated in setUpClass

    def read_from_client(self):
        if len(self.from_client_channel) == 0:
            return ""
        else:
            return self.from_client_channel.pop(0)

    def write_to_client(self, rawdata):
        self.to_client_channel.append(rawdata)
        return True

    def testEHLO(self):
        client_request = 'EHLO kitty.tw'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        fptr(terms[1:])
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('502', self.to_client_channel[0])

    def testBanner(self):
        log_desc('Server should response banner at beginning')
        executed = self.smtpu.banner('unit.test.com.tw',
                                     'Welcome to Safety Net')
        self.assertIn('220', executed)
        self.smtpu.banner('unit.test.com.tw',
                          'Welcome to Safety Net',
                          self.write_to_client)
        self.assertEqual(1, len(self.to_client_channel))
        self.assertIn('220', self.to_client_channel[0])

    def testHELO(self):
        client_request = 'HELO kitty.tw'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        fptr(terms[1:])
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('250', self.to_client_channel[0])
        self.assertIn('Hello', self.to_client_channel[0])
        self.assertIn('kitty', self.to_client_channel[0])

    def testHELP(self):
        client_request = 'HELP'
        log_desc(client_request)
        fptr = self.smtpu.command(client_request,
                                  None,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        fptr(None)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('211', self.to_client_channel[0])
        self.assertIn('helo', self.to_client_channel[0])
        self.assertIn('ehlo', self.to_client_channel[0])
        self.assertIn('mail', self.to_client_channel[0])
        self.assertIn('rcpt', self.to_client_channel[0])

    def testNOOP(self):
        client_request = 'NOOP'
        log_desc(client_request)
        fptr = self.smtpu.command(client_request,
                                  None,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        fptr(None)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('250', self.to_client_channel[0])

    def testQUIT(self):
        client_request = 'QUIT'
        log_desc(client_request)
        fptr = self.smtpu.command(client_request,
                                  None,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_code = fptr(None)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('221', self.to_client_channel[0])
        self.assertEqual(-1, return_code)

    def testVRFY(self):
        client_request = 'VRFY'
        log_desc(client_request)
        fptr = self.smtpu.command(client_request,
                                  None,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_code = fptr(None)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('502', self.to_client_channel[0])
        self.assertEqual(0, return_code)

    def testMAIL_nospace(self):
        client_request = 'mail from:<user@hello.world.com>'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        self.assertIn('user@hello.world.com', self.smtpu.mail_from)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('250', self.to_client_channel[0])
        self.assertIn('user@hello.world.com', self.to_client_channel[0])

    def testMAIL_withspace(self):
        client_request = 'mail from: user@hello.world.com'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        self.assertIn('user@hello.world.com', self.smtpu.mail_from)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('250', self.to_client_channel[0])
        self.assertIn('user@hello.world.com', self.to_client_channel[0])

    def testRCPT_one(self):
        client_request = 'rcpt to:kitty@hello.world.com'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        self.assertIn('kitty@hello.world.com', self.smtpu.recp_to)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('250', self.to_client_channel[0])
        self.assertIn('kitty@hello.world.com', self.to_client_channel[0])

    def testRCPT_morethanone(self):
        client_request = 'rcpt to:kitty@hello.world.com'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        #
        client_request = 'rcpt to:dennial@hello.world.com'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        self.assertEqual(len(self.to_client_channel), 2)
        self.assertIn('250', self.to_client_channel[0])
        self.assertIn('kitty@hello.world.com', self.to_client_channel[0])
        self.assertIn('kitty@hello.world.com', self.smtpu.recp_to)
        self.assertIn('250', self.to_client_channel[1])
        self.assertIn('dennial@hello.world.com', self.smtpu.recp_to)
        self.assertIn('dennial@hello.world.com', self.to_client_channel[1])

    def testDATA_withoutMailFrom(self):
        client_request = 'DATA'
        log_desc(client_request)
        fptr = self.smtpu.command(client_request,
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(None)
        self.assertEqual(-1, return_value)
        for i in self.to_client_channel:
            log_debug(i)
        self.assertEqual(len(self.to_client_channel), 1)
        self.assertIn('503', self.to_client_channel[0])

    def testDATA_withoutRcptTo(self):
        client_request = 'MAIL FROM:<user@hello.world.com>'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        client_request = 'DATA'
        log_desc(client_request)
        log_desc("with content below")
        for i in self.from_client_channel:
            log_desc(repr(i))
        fptr = self.smtpu.command(client_request,
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(None)
        self.assertEqual(-1, return_value)
        self.assertEqual(len(self.to_client_channel), 2)
        self.assertIn('250', self.to_client_channel[0])
        self.assertIn('503', self.to_client_channel[1])

    def testDATA_4Lines(self):
        client_request = 'MAIL FROM:<user@hello.world.com>'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        client_request = 'rcpt to:kitty@hello.world.com'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(0, return_value)
        client_request = 'DATA'
        log_desc(client_request)
        log_desc("with payload content below")
        for i in self.from_client_channel:
            log_desc(repr(i))
        fptr = self.smtpu.command(client_request,
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(None)
        self.assertEqual(1, return_value)
        self.assertEqual(len(self.to_client_channel), 4)
        log_desc("Server has Responsed to Client in sequence")
        for i in self.to_client_channel:
            log_desc(repr(i))
        log_desc("content to saved as below")
        log_desc(repr(self.smtpu.msg))
        #
        self.to_client_channel = list()  # clean up
        client_request = 'QUIT'
        log_desc(client_request)
        terms = client_request.split(' ')
        fptr = self.smtpu.command(terms[0],
                                  self.read_from_client,
                                  self.write_to_client)
        self.assertIsNotNone(fptr)
        return_value = fptr(terms[1:])
        self.assertEqual(-1, return_value)
        log_desc("Server Responsed")
        log_desc(repr(self.to_client_channel[0]))
        self.assertIn('221', self.to_client_channel[0])


if __name__ == '__main__':
    unittest.main()
