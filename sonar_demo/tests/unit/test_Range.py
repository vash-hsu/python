#!/usr/bin/env python

import unittest
from util.Range import Range
from util.Range import div_mod


def log_print(label, message):
    print("%s: %s" % (label,  message))


def log_title(message):
    log_print('CASE', message)


def log_desc(message):
    log_print('DESC', message)


class BoundaryTest4Range(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.my_start, cls.my_stop, cls.my_step = (3, 19, 3)

    def setUp(self):
        print('')
        title = '.'.join(self.id().split('.')[1:])
        log_title(title)

    # def tearDown(self):
    #     print

    def test_hardcode_happy_path_index(self):
        my_start, my_stop, my_step = (3, 17, 4)
        common_example = Range(my_start, my_stop, my_step)
        '''
        [0, 1, 2, 3] = [3, 7, 11, 15]
        '''
        self.assertEqual(common_example[0], 3)
        self.assertEqual(common_example[1], 7)
        self.assertEqual(common_example[2], 11)
        self.assertEqual(common_example[3], 15)
        with self.assertRaises(IndexError):
            example = common_example[4]

    def test_hardcode_happy_path_slice(self):
        my_start, my_stop, my_step = (3, 17, 4)
        common_example = Range(my_start, my_stop, my_step)
        '''
        [0, 1, 2, 3] = [3, 7, 11, 15]
        [0:2] = [3, 7]
        [2:4] = [11, 15]
        [3:5] = [15, ]
        '''
        self.assertEqual(common_example[0:2], [3, 7])
        self.assertEqual(common_example[2:4], [11, 15])
        self.assertEqual(common_example[3:5], [15, ])

    def test_RAT_happy_path_index(self):
        my_start, my_stop, my_step = (self.my_start, self.my_stop, self.my_step)
        common_example = Range(my_start, my_stop, my_step)
        for i in xrange(1, (my_stop-my_start)/my_step):
            result = common_example[i]
            expected = i*my_step + my_start
            msg = ['to validate', str(result), 'whose offset', "[%d]" % i,
                   'exists in', str(list(common_example)),
                   "equivalent to %d" % expected]
            log_desc(' '.join(msg))
            self.assertIn(result, common_example)
            self.assertEqual(result, expected)

    def test_RAT_happy_path_slice(self):
        my_start, my_stop, my_step = (self.my_start, self.my_stop, self.my_step)
        common_example = Range(my_start, my_stop, my_step)
        for i in xrange(1, (my_stop-my_start)/my_step):
            result = common_example[i:i+2]
            for j in result:
                msg = ['to validate', str(j), 'from', str(result),
                       'whose slice', "[%d:%d]" % (i, i+2),
                       'exists in', str(list(common_example))]
                log_desc(' '.join(msg))
                self.assertIn(j, common_example,
                              "%s, whose slice [%d:%d] is not defined in %s" %
                              (str(j), i, i+2, str(list(common_example)))
                )

    def test_FAST_upper_bound_slice(self):
        my_start, my_stop, my_step = (self.my_start, self.my_stop, self.my_step)
        common_example = Range(my_start, my_stop, my_step)
        upper_bound = (my_stop - my_start)/my_step + 1
        for i in xrange(upper_bound - 1, upper_bound):
            result = common_example[i:i+2]
            for j in result:
                msg = ['to validate', str(j), 'from', str(result),
                       'whose slice', "[%d:%d]" % (i, i+2),
                       'exists in', str(list(common_example))]
                log_desc(' '.join(msg))
                self.assertIn(j, common_example,
                              "%s, whose slice [%d:%d] is not defined in %s" %
                              (str(j), i, i+2, str(list(common_example)))
                )

    def test_FAST_lower_bound_slice(self):
        my_start, my_stop, my_step = (self.my_start, self.my_stop, self.my_step)
        common_example = Range(my_start, my_stop, my_step)
        i = 0
        result = common_example[i:i+2]
        for j in result:
            msg = ['to validate', str(j), 'from', str(result),
                   'whose slice', "[%d:%d]" % (i, i+2),
                   'exists in', str(list(common_example))]
            log_desc(' '.join(msg))
            self.assertIn(j, common_example,
                          "%s, whose slice [%d:%d] is not defined in %s" %
                          (str(j), i, i+2, str(list(common_example)))
            )

    def test_hardcode_div_mod(self):
        self.assertEqual(div_mod(10, 3), (3, 1))
        self.assertEqual(div_mod(10, 2), (5, 0))

    def test_hardcode_range_len_getitem(self):
        example = Range(1)
        self.assertEqual(len(example), 1)
        self.assertEqual(example[0], 0)
        example = Range(2)
        self.assertEqual(len(example), 2)
        self.assertEqual(example[0], 0)
        self.assertEqual(example[1], 1)

    def test_FET_range_empty_from0to0(self):
        # empty set, where 0 ~ 0
        parameter = 0
        example = Range(parameter)
        expected = 0
        msg = ['to validate length of', str(list(example)),
               'from Range(%d)' % parameter,
               'which should be equal to %d' % expected]
        log_desc(' '.join(msg))
        self.assertEqual(len(example), expected)

    def test_FET_range_minimal_set(self):
        # minimal set, where 0 ~ 1
        example = Range(0, 1)
        expected = 1
        msg = ['to validate length of', str(list(example)),
               'from Range(0, 1)',
               'which should be equal to %d' % expected]
        log_desc(' '.join(msg))
        self.assertEqual(len(example), expected)

    def test_FET_range_large_step(self):
        # minimal set, where step larger than distance between start and end
        example = Range(1, 3, 4)
        expected = 1
        msg = ['to validate length of', str(list(example)),
               'from Range(1, 3, 4)',
               'which should be equal to %d' % expected]
        log_desc(' '.join(msg))
        self.assertEqual(len(example), expected)

    def test_FET_range_out_of_order(self):
        # empyt set, where out-of-order
        example = Range(2, 1)
        expected = 0
        msg = ['to validate length of', str(list(example)),
               'from Range(2, 1)',
               'which should be equal to %d' % expected]
        log_desc(' '.join(msg))
        self.assertEqual(len(example), expected)


if __name__ == '__main__':
    unittest.main()
