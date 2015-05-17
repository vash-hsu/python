#!/usr/bin/env python

import unittest
from sec import brute_force
from sec import module
import hashlib, math, random


# SUT
from sec.brute_force import guess_by_realtime_brute_force, \
                        guess_by_rainbowtable, \
                        RainbowTable, \
                        rainbow_table_fill, \
                        guess_by_rainbowtable_reuse
                        


class Brute_Force_RainbowTableReuse_test(unittest.TestCase):
  def setUp(self):
    pass
  def tearDown(self):
    pass
  def test_FAST_1_rainbow_reuse_passcode_digit_6_multi_hit(self):
    "FAST: guess_by_rainbowtable_reuse success guess the digit 6-1 passcode"
    _digit = 6
    # build rainbow table first
    rainbow_table = dict()
    rainbow_table_fill(rainbow_table, _digit)
    rainbow_table_reusable = RainbowTable(rainbow_table)
    del rainbow_table
    # several run for testing
    for i in range(1,_digit+1):
      user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
      user_shadow   = hashlib.sha1(user_passcode).hexdigest()
      answer = guess_by_rainbowtable_reuse(rainbow_table_reusable, user_shadow)
      self.assertEqual(user_passcode, answer)
  def test_FET_1_rainbow_reuse_passcode_digit_6_multi_nothit(self):
    "FET: guess_by_rainbowtable_reuse fail to guess the digit 6-1 passcode"
    _digit = 6
    # build rainbow table first
    rainbow_table = dict()
    rainbow_table_fill(rainbow_table, _digit)
    rainbow_table_reusable = RainbowTable(rainbow_table)
    del rainbow_table
    # several run for testing
    for i in range(1,_digit+1):
      user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
      user_shadow   = hashlib.sha1(user_passcode).hexdigest()
      answer = guess_by_rainbowtable_reuse(rainbow_table_reusable, user_shadow)
      self.assertEqual(user_passcode, answer)
# 
class Brute_Force_RainbowTable_test(unittest.TestCase):
  def setUp(self):
    pass
  def tearDown(self):
    pass
  def test_FAST_1_rainbow_lookup_passcode_1_hit(self):
    "FAST: guess_by_rainbowtable success guess the digit 1 passcode"
    _digit = 1
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_rainbowtable(len(user_passcode), user_shadow)
    self.assertEqual(user_passcode, answer)
  def test_FAST_2_rainbow_lookup_passcode_6_hit(self):
    "FAST: guess_by_rainbowtable success guess the digit 6 passcode"
    _digit = 6
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_rainbowtable(len(user_passcode), user_shadow)
    self.assertEqual(user_passcode, answer)
  def test_FET_1_rainbow_lookup_passcode_6_nothit(self):
    "FET: guess_by_rainbowtable fail guess the digit 6-1 passcode"
    _digit = 6
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_rainbowtable(len(user_passcode)-1, user_shadow)
    self.assertEqual(None, answer)

class Brute_Force_RealTime_Test(unittest.TestCase):
  def setUp(self):
    pass
  def tearDown(self):
    pass
  def test_FAST_1_realtime_bf_passcode_1_hit(self):
    "FAST: guess_by_realtime_brute_force success guess the digit 1 passcode"
    _digit = 1
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_realtime_brute_force(len(user_passcode), user_shadow)
    self.assertEqual(user_passcode, answer)
  def test_FAST_2_realtime_bf_passcode_5_hit(self):
    "FAST: guess_by_realtime_brute_force success guess the digit 5 passcode"
    _digit = 5
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_realtime_brute_force(len(user_passcode), user_shadow)
    self.assertEqual(user_passcode, answer)
  def test_FAST_3_realtime_bf_passcode_6_hit(self):
    "FAST: guess_by_realtime_brute_force success guess the digit 6 passcode"
    _digit = 6
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_realtime_brute_force(len(user_passcode), user_shadow)
    self.assertEqual(user_passcode, answer)
  def test_FET_1_realtime_bf_passcode_5_nothit(self):
    "FAST: guess_by_realtime_brute_force fail to guess the digit 5-1 passcode"
    _digit = 5
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    answer = guess_by_realtime_brute_force(len(user_passcode)-1, user_shadow)
    self.assertEqual(None, answer)

if __name__ == '__main__':
  testruner  = unittest.TextTestRunner(verbosity=2)
  testloader = unittest.TestLoader()
  
  list_testsuit = list()
  for i in [Brute_Force_RealTime_Test,
            Brute_Force_RainbowTable_test,
            Brute_Force_RainbowTableReuse_test]:
    testsuit = testloader.loadTestsFromTestCase(i)
    list_testsuit.append(testsuit)
  alltests = unittest.TestSuite(list_testsuit)
  
  testruner.run(alltests)