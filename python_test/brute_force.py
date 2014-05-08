#!/usr/bin/env python

import hashlib
import math
import random

CONST_UPPER_BOUND = 999999

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

def rainbow_table_fill(table_export, digit_max_length):
  for i in range(1, int (math.pow(10, digit_max_length)) ):
    str_num = str(i)
    str_sha1 = hashlib.sha1(str_num).hexdigest()
    table_export[str_sha1] = str_num

def rainbow_table_lookup(rainbow_table, user_shadow):
  try:
    return rainbow_table[user_shadow]
  except KeyError:
    return None

def guess_by_rainbowtable_reuse(table_reusable, user_shadow):
  return table_reusable.find(user_shadow)

def guess_by_rainbowtable(digit_max_length, user_shadow):
  rainbow_table = dict()
  # setup
  rainbow_table_fill(rainbow_table, digit_max_length)
  # guess
  answer = rainbow_table_lookup(rainbow_table, user_shadow)
  # report
  return answer

def guess_by_realtime_brute_force(digit_max_length, user_shadow):
  for i in range(1, int (math.pow(10, digit_max_length)) ):
    str_num = str(i)
    str_sha1 = hashlib.sha1(str_num).hexdigest()
    if str_sha1 == user_shadow:
      return str_num
  return None

def tell_answer(answer):
  if None == answer:
    return 'not found'
  return answer

def examples_for_password_guessing():
  # setup
  rainbow_table = dict()
  rainbow_table_fill(rainbow_table, len(str(CONST_UPPER_BOUND)))
  rainbow_table_reusable = RainbowTable(rainbow_table)
  # guess many many times
  for i in range(1,11):
    print '----- Run', i
    # ready
    user_passcode = str( random.randint(1,CONST_UPPER_BOUND) )
    user_shadow   = hashlib.sha1(user_passcode).hexdigest()
    print '* User input', user_passcode, 'as SHA1', user_shadow
    # go
    print '* Try to lookup from rainbow table -->', 
    #answer = rainbow_table_reusable.find(user_shadow)
    answer = guess_by_rainbowtable_reuse(rainbow_table_reusable, user_shadow)
    print tell_answer(answer)
    # go
    print '* Try to lookup from brute force -->', 
    answer = guess_by_realtime_brute_force(len(user_passcode), user_shadow)
    print tell_answer(answer)
    
def example_for_password_guessing():
  # ready
  user_passcode = str( random.randint(1,CONST_UPPER_BOUND) )
  user_shadow   = hashlib.sha1(user_passcode).hexdigest()
  print '* User input', user_passcode, 'as SHA1', user_shadow
  # go
  print '* Try to lookup from rainbow table -->', 
  answer = guess_by_rainbowtable(len(user_passcode), user_shadow)
  print tell_answer(answer)
  # go
  print '* Try to lookup from brute force -->', 
  answer = guess_by_realtime_brute_force(len(user_passcode), user_shadow)
  print tell_answer(answer)

def main():
  print "---------- example for password guessing"
  #example_for_password_guessing()
  examples_for_password_guessing()


if __name__ == '__main__':
  main()