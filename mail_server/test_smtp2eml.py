#!/usr/bin/env python

import unittest


def log_print(label, message):
    print("%s: %s" % (label,  message))


def log_title(message):
    log_print('CASE', message)


def log_desc(message):
    log_print('DESC', message)


def log_debug(message):
    log_print('DEBUG', message)


class smtp2emlTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)


if __name__ == '__main__':
    unittest.main()
