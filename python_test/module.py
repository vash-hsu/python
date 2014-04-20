#!/usr/bin/env python

__all__ = ["find"]

def find(compare, argsin):
  # find max or min?
  if compare.lower() == 'max':
    func_compare = greater_than
  elif compare.lower() == 'min':
    func_compare = less_than
  else:
    errmsg = "unrecognized:", compare
    return None
  # data is acceptable?
  if type(argsin) == str or type(argsin) == list:
    return minmax(func_compare, argsin)
  elif type(argsin) == dict:
    key = minmax(func_compare, argsin.keys())
    return key, argsin[key]
  else:
    #errmsg = "deny type:", type(argsin)
    return None

def minmax(test, listin):
  res = listin[0]
  for element in listin[1:]:
    if test(element, res):
      res = element
  return res

def less_than(x, y):
  return x < y
def greater_than(x, y):
  return x > y

# self test code
if __name__ == '__main__':
  test_feed_list = [4, 2, 1, 5, 6, 3]
  test_feed_tuple = (4, 2, 1, 5, 6, 3)
  test_feed_dict = {4:'four', 2:'two', 1:'one', 5:'five', 6:'six', 3:'three'}
  test_feed_string = 'spam'
  
  print "== test list", test_feed_list
  print "max", find('max', test_feed_list)
  print "min", find('min', test_feed_list)
  print "== test tuple", test_feed_tuple
  print "max", find('max', test_feed_tuple)
  print "min", find('min', test_feed_tuple)
  print "== test dict", test_feed_dict
  print "max", find('max', test_feed_dict)
  print "min", find('min', test_feed_dict)
  print "== test string", test_feed_string
  print "max", find('max', test_feed_string)
  print "min", find('min', test_feed_string)