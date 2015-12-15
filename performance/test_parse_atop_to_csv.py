#!/usr/bin/env python

import unittest
from parse_atop_to_csv import *


def log_print(label, message):
    print("%s: %s" % (label,  message))


def log_title(message):
    log_print('CASE', message)


def log_desc(message):
    log_print('DESC', message)


def log_debug(message):
    log_print('DEBUG', message)


class UtilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)

    def tearDown(self):
        pass

    def test_system_get_stdout(self):
        log_desc('system_get_stdout() test command return single-line output')
        command = 'echo hello world'
        result = system_get_stdout(command)
        self.assertEqual(result, ['hello world'])

    def test_iter_system_get_stdout(self):
        log_desc('iter_system_get_stdout() test for i in')
        command = 'echo hello && echo world && echo end'
        expected = ['hello', 'world', 'end']
        offset = 0
        for i in iter_system_get_stdout(command):
            self.assertEqual(i, expected[offset])
            offset += 1

    def test_convert_data_unit_to_pure_number(self):
        # data, unit, unit_to='g', digit=3
        log_desc('conversion between g, m, k and %')
        self.assertEqual(convert_data_unit_to_pure_number(1, 'g', 'm', 3),
                         1024)
        self.assertEqual(convert_data_unit_to_pure_number(0.5, 'm', 'k', 3),
                         512)
        self.assertEqual(convert_data_unit_to_pure_number(0.1, 'g', 'g', 3),
                         0.1)
        self.assertEqual(convert_data_unit_to_pure_number(15.1234, '%', '', 4),
                         0.1512)
        self.assertEqual(convert_data_unit_to_pure_number(50, 'm'),
                         0.049)
        self.assertEqual(convert_data_unit_to_pure_number(50, 'x'),
                         0)

    def test_convert_string_to_pure_number(self):
        log_desc('conversion from 15% to 0.15 and 900m to 0.879')
        self.assertEqual(convert_string_to_pure_number('15%'), 0.15)
        self.assertEqual(convert_string_to_pure_number('900m'), 0.879)
        self.assertEqual(convert_string_to_pure_number('900'), 900)
        self.assertEqual(convert_string_to_pure_number('0.123456'), 0.123)

    def test_convert_exponent(self):
        log_desc('conversion from 1.23E+3 to 1230.3')
        self.assertEqual(convert_exponent('1.23E+3'), '1230.0')
        self.assertEqual(convert_exponent('1.23E-3'), '0.001')

    def test_index_keyword_in_text(self):
        log_desc('mem is offset 1 in \"CPU MEM DSK\"')
        self.assertEqual(index_keyword_in_text('cpu', 'CPU MEM DSK'), 0)
        self.assertEqual(index_keyword_in_text('Mem', 'CPU MEM DSK'), 1)
        self.assertEqual(index_keyword_in_text('DSK', 'CPU MEM DSK',
                                               sensitive=True), 2)
        self.assertEqual(index_keyword_in_text('dsk', 'CPU MEM DSK',
                                               sensitive=True), -1)

    def test_convert_string_to_timestamp(self):
        log_desc('conversion from 2010-11-16 20:10:58 to 1289909458')
        self.assertEqual(convert_string_to_timestamp('2010-11-16 20:10:58'),
                         1289909458)
        self.assertEqual(convert_string_to_timestamp('2010/11/16 20:10:58'),
                         1289909458)
        self.assertEqual(convert_string_to_timestamp('2010-11-16'), -1)

    def test_convert_timestamp_to_string(self):
        log_desc('conversion from 1289909458 to 2010-11-16 20:10:58')
        self.assertEqual(convert_timestamp_to_string(1289909458),
                         '2010-11-16 20:10:58')

if __name__ == '__main__':
    unittest.main()
