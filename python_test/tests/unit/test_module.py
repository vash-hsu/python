#!/usr/bin/env python

# https://docs.python.org/2.6/library/unittest.html

import unittest
from sec import module
import os, sys, getopt

# test cases for module
class ModuleTest(unittest.TestCase):
  test_feed_list   = None
  test_feed_tuple  = None
  test_feed_dict   = None
  test_feed_string = None
  def setUp(self):
    self.test_feed_list   = [4, 2, 1, 5, 6, 3]
    self.test_feed_tuple  = (4, 2, 1, 5, 6, 3)
    self.test_feed_dict   = {4:'four', 2:'two', 1:'one',
                             5:'five', 6:'six', 3:'three'}
    self.test_feed_string = 'spam'
  def tearDown(self):
    self.test_feed_list   = None
    self.test_feed_tuple  = None
    self.test_feed_dict   = None
    self.test_feed_string = None
  def test_find_list_max(self):
    "FAST: parse list and return max elemtnt"
    self.assertEqual(6, module.find("max", self.test_feed_list))
  def test_find_list_min(self):
    "FAST: parse list and return min element"
    self.assertEqual(1, module.find("min", self.test_feed_list))
  def test_find_dict_max(self):
    "FAST: parse dict and return key, value for max key"
    self.assertEqual((6, 'six'), module.find("max", self.test_feed_dict))
  def test_find_dict_min(self):
    "FAST: parse dict and return key, value for min key"
    self.assertEqual((1, 'one'), module.find("min", self.test_feed_dict))
  def test_find_str_max(self):
    "FAST: parse str and return max character"
    self.assertEqual('s', module.find("max", self.test_feed_string))
  def test_find_str_min(self):
    "FAST: parse str and return min character"
    self.assertEqual('a', module.find("min", self.test_feed_string))
  def test_find_with_unsupport_datatype(self):
    "FET: parse tuple, which is not supported"
    self.assertEqual(None, module.find("min", self.test_feed_tuple))
  def test_find_with_unsupport_compare_method(self):
    "FET: parse with mid, which is not supported"
    self.assertEqual(None, module.find("mid", self.test_feed_tuple))
  def test_find_demo_failure(self):
    "FET: force fail to demo test failure"
    self.fail("let test fail")

def print_usage(name):
  print "USAGE:"
  print "to list test cases:\n\t%s -l" % (name)
  print "to execute all test cases:\n\t%s" % (name)

def dump_testcase_list():
  # test loader
  testloader      = unittest.TestLoader()
  list_testcases  = testloader.getTestCaseNames(ModuleTest)
  total_case_nums = len(list_testcases)
  case_counter    = 0
  for i in list_testcases:
    case_counter += 1
    print "%d/%d\t%s" %(case_counter, total_case_nums, i)

if __name__ == "__main__":
  # ==  parse parameter ==
  scriptfilename = os.path.split(sys.argv[0])[1]
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hl")
  except getopt.GetoptError:
    print_usage(scriptfilename)
    sys.exit(-1)
  # ==  decide what's next ==
  todo_list_testcase = False
  for opt, arg in opts:
    if opt == '-l':
      todo_list_testcase = True
    elif opt == '-h':
      print_usage(scriptfilename)
      sys.exit(-1)
  if todo_list_testcase:
    dump_testcase_list()
  else:
    # -- basic --
    #unittest.main()
    #unittest.main(verbosity=3)
    # -- test suit --
    #suite = unittest.TestLoader().loadTestsFromTestCase(ModuleTest)
    #unittest.TextTestRunner(verbosity=2).run(suite)
    #print suite.countTestCases()
    # -- test loader --
    testloader = unittest.TestLoader()
    testsuit = testloader.loadTestsFromTestCase(ModuleTest)
    testruner = unittest.TextTestRunner(verbosity=2)
    testruner.run(testsuit)