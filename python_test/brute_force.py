#!/usr/bin/env python

import hashlib, math, random
import sys, getopt

# https://docs.python.org/2/library/profile.html
# https://docs.python.org/2/library/random.html
# https://docs.python.org/2/library/math.html
# https://docs.python.org/2/library/hashlib.html
# https://docs.python.org/2/library/getopt.html

CONST_DIGIT_SIZE_MAX = 6
CONST_LOOP_MAX       = 10

def print_usage():
  print '''Usage:
  
== format ==
  -l <loop counter> -s <digit size> -r  
== scenario ==
  -l 10 -s 5 -r
     loop 10 times, digit range from 1 ~ 99999, reuse rainbow table
  -l 5 -s 4
     loop 5 times, digit range from 1 ~ 9999, create rainbow table for each run
== hint ==
  python -m cProfile -s tottime
  python -m cProfile -s cumtime
      -m cProfile, identify performance matrix with small overhead
      -s tottime, sorted by total time spent in the given function
                  (and excluding time made in calls to sub-functions)
      -s cumtime, sorted by cumulative time spent in this and all subfunctions
                  (accurate even for recursive functions)
'''

class RainbowTable:
  def __init__(self, table_import):
    self._rainbow_table = dict()
    if type(table_import) == dict:
      for i, j in table_import.iteritems():
        self._rainbow_table[i] = j
  def insert(self, shadow, plaintext):
    self._rainbow_table[shadow] = plaintext
  def purge(self, shadow):
    del self._rainbow_table[shadow]
  def find(self, shadow):
    try:
      return self._rainbow_table[shadow]
    except KeyError:
      return None
  def size(self):
    return len(self._rainbow_table)
  def destroy(self):  
    self._rainbow_table = dict()

def rainbow_table_fill(table_export, _digit_size):
  for i in range(1, int (math.pow(10, _digit_size)) ):
    str_num = str(i)
    str_sha1 = hashlib.sha1(str_num).hexdigest()
    table_export[str_sha1] = str_num

def rainbow_table_lookup(rainbow_table, user_shadow):
  try:
    return rainbow_table[user_shadow]
  except KeyError:
    return None

def guess_by_rainbowtable_reuse(_table_reusable, _user_shadow):
  return _table_reusable.find(_user_shadow)

def guess_by_rainbowtable(_digit_size, _user_shadow):
  rainbow_table = dict()
  # setup
  rainbow_table_fill(rainbow_table, _digit_size)
  # guess
  answer = rainbow_table_lookup(rainbow_table, _user_shadow)
  # free
  del rainbow_table
  # report
  return answer

def guess_by_realtime_brute_force(_digit_size, _user_shadow):
  for i in range(1, int (math.pow(10, _digit_size)) ):
    str_num = str(i)
    str_sha1 = hashlib.sha1(str_num).hexdigest()
    if str_sha1 == _user_shadow:
      return str_num
  return None

def tell_answer(answer):
  if None == answer:
    return 'not found'
  return answer

def example_for_password_guessing(_loop, _digit, _reuse):
  rainbow_table_reusable = None
  # prepare rainbow table?
  if _reuse == True:
    rainbow_table = dict()
    rainbow_table_fill(rainbow_table, _digit)
    rainbow_table_reusable = RainbowTable(rainbow_table)
    del rainbow_table
  # guess password by rainbow table and brute force for loop
  for i in range(1,_loop+1):
    print '----- Run', i
    # ready
    user_passcode = str( random.randint(1, int(math.pow(10, _digit))-1) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    print '* Random Gen User Digit Passcode', user_passcode, 'as SHA1', user_shadow
    # go
    print '* Try to lookup from rainbow table -->',
    if _reuse == True:
      answer = guess_by_rainbowtable_reuse(rainbow_table_reusable, user_shadow)
    else:
      answer = guess_by_rainbowtable(_digit, user_shadow)
    print tell_answer(answer)
    # go
    print '* Try to lookup from brute force   -->', 
    answer = guess_by_realtime_brute_force(_digit, user_shadow)
    print tell_answer(answer)
  
def main():
  if len(sys.argv) == 0:
    print_usage()
    sys.exit(0)
  try:
    optlist, args = getopt.getopt(sys.argv[1:], 'l:s:r')
  except getopt.GetoptError as err:
    print 'ERROR:', str(err)
    print_usage()
    sys.exit(-1)
  # internal data member with default value
  reuse_rt     = False
  loop_counter = None
  digit_size   = None
  # fill
  for name, value in optlist:
    if '-l' == name:
      loop_counter = int(value)
    elif '-s' == name:
      digit_size = int(value)
    elif '-r' == name:
      reuse_rt = True
    else:
      print "Vitali? Italia?"
  # check & reset
  if loop_counter == None or digit_size == None:
    print_usage()
    sys.exit(0)
  if loop_counter > CONST_LOOP_MAX:
    loop_counter = CONST_LOOP_MAX
    print 'WARN: reset <loop counter> to', loop_counter
  if digit_size > CONST_DIGIT_SIZE_MAX:
    digit_size = CONST_DIGIT_SIZE_MAX
    print 'WARN: reset  <digit size> to', digit_size
  # execute
  example_for_password_guessing(loop_counter, digit_size, reuse_rt)


if __name__ == '__main__':
  main()