#!/usr/bin/env python

# https://docs.python.org/2.6/library/unittest.html
# https://pypi.python.org/pypi/coverage

import unittest
import os, sys, getopt

__all__ = ['prase_argv_to_param']

# input
#    type(argv) == list
# inpout/output
#    type(param) == dict; key --> value (list)
#    type(flag) == dict; key --> True/False (list)
# output
#    return True or False
#    type(arglist) == list
def prase_argv_to_param(argv, param, flag, arglist):
  # pre-condition
  if len(argv) == 0 or len(argv[0]) == 0:
    return False
  # prepare
  list4param = list()
  list4flag = list()
  str_options = ''
  if type(param) == dict:
    list4param = param.keys()
  if type(flag) == dict:
    list4flag  = flag.keys()
  if (len(list4param) > 0 or len(list4flag) > 0):
    str_options = ':'.join(list4param)
    if (len(list4param) > 0):
      str_options += ':'
    str_options += ''.join(list4flag)
  # getopt
  try:
    opts, args = getopt.getopt(argv, str_options)
  except getopt.GetoptError:
    #print "DM: getopt.GetoptError"
    return False
  # action for each
  for opt, arg in opts:
    opt = opt[1:] # tream -, '-h' --> 'h'
    if opt in list4param:
      param[opt].append(arg)
    elif opt in list4flag:
      flag[opt].append(True)
    else:
      return False
  if len(args) > 0 and type(arglist) == list:
    for i in args:
      arglist.append(i)
  return True


# test cases for module
class ArgvTest(unittest.TestCase):
  def setUp(self):
    'hello setup'
  def tearDown(self):
    'hello teardown'
  def test_RAT_all_flag_param(self):
    "RAT: -h -v -i input -o output"
    # in
    argv  = ['-h', '-v', '-i', 'input', '-o', 'output']
    # out
    param = { 'i': list(), 'o': list() }
    flag  = { 'h': list(), 'v': list() }
    # do
    prase_argv_to_param(argv, param, flag, None)
    # check
    self.assertEqual(flag['h'][0], True)
    self.assertEqual(flag['v'][0], True)
    self.assertEqual(len(param['i']), 1)
    self.assertEqual(len(param['o']), 1)
    self.assertEqual(param['i'], ['input'])
    self.assertEqual(param['o'], ['output'])
  def test_FAST_repeated_more_than_once_flag(self):
    "FAST: -h -v -h -v -h"
    # in
    linein = "-h -v -h -v -h"
    argv  = linein.split(' ')
    # out
    flag  = { 'h': list(), 'v': list() }
    # do
    prase_argv_to_param(argv, None, flag, None)
    # check
    self.assertEqual(len(flag['h']), 3)
    self.assertEqual(len(flag['v']), 2)
    self.assertEqual(flag['h'][-1], True)
    self.assertEqual(flag['v'][-1], True)
  def test_FAST_repeated_consequence_flag(self):
    "FAST: -vvv -hh"
    # in
    linein = "-vvv -hh"
    argv  = linein.split(' ')
    # out
    flag  = { 'h': list(), 'v': list() }
    # do
    prase_argv_to_param(argv, None, flag, None)
    # check
    self.assertEqual(len(flag['h']), 2)
    self.assertEqual(len(flag['v']), 3)
    self.assertEqual(flag['h'][-1], True)
    self.assertEqual(flag['v'][-1], True)
  def test_FAST_repeated_param(self):
    "FAST: -i 1 -o one -i 2 -o two -i 3 -o three"
    # in
    linein = "-i 1 -o one -i 2 -o two -i 3 -o three"
    argv  = linein.split(' ')
    # out
    param = { 'i': list(), 'o': list() }
    # do
    prase_argv_to_param(argv, param, None, None)
    # check
    self.assertEqual(len(param['i']), 3)
    self.assertEqual(len(param['o']), 3)
    self.assertEqual(param['i'], ['1', '2', '3'])
    self.assertEqual(param['o'], ['one', 'two', 'three'])
  def test_FAST_lots_parameters(self):
    "FAST: aaa bbb ccc ddd"
    # in
    linein = "aaa bbb ccc ddd"
    argv  = linein.split(' ')
    # out
    para = list()
    # do
    returnValue = prase_argv_to_param(argv, None, None, para)
    # check
    self.assertEqual(returnValue, True)
    self.assertEqual(len(para), 4)
    self.assertEqual(para, ['aaa', 'bbb', 'ccc', 'ddd'])
  def test_FET_undef_param(self):
    "FET: -i input -w unknown"
    # in
    linein = "-i input -w unknown"
    argv  = linein.split(' ')
    # out
    param = { 'i': list(), 'o': list() }
    # do
    return_value = prase_argv_to_param(argv, param, None, None)
    # check
    self.assertEqual(return_value, False)
  def test_FET_missing_part_param(self):
    "FET: -i -o output"
    # in
    linein = "-i -o output"
    argv  = linein.split(' ')
    # out
    param = { 'i': list(), 'o': list() }
    # do
    return_value = prase_argv_to_param(argv, param, None, None)
    # check
    self.assertEqual(return_value, True)
    self.assertEqual(param['i'], ['-o'])
  def test_FET_no_parameters(self):
    "FET: no parameters"
    # in
    linein = ""
    argv  = linein.split(' ')
    # out
    param = { 'i': list(), 'o': list() }
    # do
    return_value = prase_argv_to_param(argv, param, None, None)
    # check
    self.assertEqual(return_value, False)

def testrun():
  testloader = unittest.TestLoader()
  testsuit = testloader.loadTestsFromTestCase(ArgvTest)
  testruner = unittest.TextTestRunner(verbosity=2)
  testruner.run(testsuit)

def testlist():
  testloader      = unittest.TestLoader()
  list_testcases  = testloader.getTestCaseNames(ArgvTest)
  total_case_nums = len(list_testcases)
  case_counter    = 0
  for i in list_testcases:
    case_counter += 1
    print "%d/%d\t%s" %(case_counter, total_case_nums, i)

def testrun_with_coverage(myself):
  commands = ['which coverage',
              'coverage erase',
              'coverage run %s -t' % (myself),
              'coverage report -m',
              'coverage erase'
             ]
  for str_command in commands:
    ret_value = os.system(str_command)
    if 0 != ret_value:
      print "ERROR(%d): %s" % (ret_value, str_command)
      break

def print_usage():
  print '''
usage     : -h -l -t

-h        : show help
-l        : lise test cases
-t        : run test cases
-tt       : run test cases with coverage

Note: how to install python coverage
for win  :
  pip install coverage
for linux:
  wget https://pypi.python.org/packages/source/c/coverage/coverage-3.7.1.tar.gz#md5=c47b36ceb17eaff3ecfab3bcd347d0df
  tar -zxvf coverage-3.7.1.tar.gz
  cd coverage-3.7.1/
  sudo python setup.py install -v
'''

if __name__ == "__main__":
  myself = sys.argv[0]
  argv = sys.argv[1:]
  flag = {'h':list(), 'l':list(), 't':list()}
  if False == prase_argv_to_param(argv, None, flag, None):
    print_usage()
    sys.exit(0)
  if len(flag['h']) > 0:
    print_usage()
  if len(flag['l']) != 0:
    testlist()
  if len(flag['t']) > 1:
    testrun_with_coverage(myself)
  elif len(flag['t']) > 0:
    testrun()
