#!/usr/bin/env python

import sys
import os

def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class ISeenYou:
    def __init__(self):
        self.instance = dict()

    def there(self, number):
        if number not in self.instance:
            self.instance[number] = 1
            return False
        else:
            self.instance[number] += 1
            return True

    def howmany(self):
        for i in sorted(self.instance.keys()):
            yield (i, self.instance[i])


def task_handle_zipper(x=0, y=0, left=0, right=0):
    my_iseeu = ISeenYou()
    if 0 not in (x, y, left, right):
        if not my_iseeu.there(left+right):
            if left != right:
                print "zip %d.zip %d.zip %d.zip" % (left+right, left, right)
            else:
                print "zip %d.zip %d.zip" % (left+right, left)
                print "ln -s %d.zip _%d.zip" % (left, right)
                print "zip -u %d.zip _%d.zip" % (left+right, right)
                print "rm _%d.zip" % right
    return left + right


def task_handle_debug(x=0, y=0, left=0, right=0):
    print "(%d, %d) = %d + %d = %d" %(x, y, left, right, left+right)
    return left + right


def pascal_triangle_adv(number, callback):
    result = list()
    if number < 1:
        return result
    for i in range(0, number):
        working = list()
        working.append(callback(i, 0, 1))
        if i == 0:
            result.append(working)
            continue
        for j in range(1, i):
            working.append(callback(i, j, result[i-1][j-1], result[i-1][j]))
        working.append(callback(i, i, 1))
        result.append(working)
    return result


def pascal_triangle_basic(number):
    result = list()
    if number < 1:
        return result
    for i in range(0, number):
        working = list()
        working.append(1)  # (x, 0)
        if i == 0:
            result.append(working)  # (0, 0)
            continue
        for j in range(1, i):
            # (x, y) = (x-1, y-1) + (x-1, y)
            working.append(result[i-1][j-1] + result[i-1][j])
        working.append(1)  # (x, y=x)
        result.append(working)
    return result


def usage(myself):
    print """Usage: %s -h
  %s  5            : print Pascal Triangle in 5 layers
  %s  7  read.txt  : zip command for file read.txt in 7 layers
""" % (myself,myself, myself)

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        usage(os.path.split(sys.argv[0])[-1])
        sys.exit(0)
    target_file = None
    layer = int(sys.argv[1]) if sys.argv[1].isdigit() else 0
    try:
        target_file = sys.argv[2] if os.path.isfile(sys.argv[2]) else None
    except IndexError:
        target_file = None
    #
    if target_file:
        print '===== pascal_triangle_adv with zipper ====='
        print "zip 1.zip %s" % target_file
        output = pascal_triangle_adv(layer, task_handle_zipper)
        for i in output:
            print i
        for i, j in ISeenYou().howmany():
            print "King: I see %d in %d times" % (i, j)
    else:
        print '===== pascal_triangle_basic ====='
        output = pascal_triangle_basic(layer)
        for i in output:
            print i
        #
        print '===== pascal_triangle_adv ====='
        output = pascal_triangle_adv(layer, task_handle_debug)
        for i in output:
            print i