#!/usr/bin/env python


# http://chimera.labs.oreilly.com/books/1230000000393/ch01.html#_keeping_the_last_n_items


from collections import deque, OrderedDict
from sys import argv, exit
import os


# 10 line_10, line_5, line_6, line_7, line_8, line_9
def search(lines, pattern, history=5):
    line_num = 0
    previous_lines = deque(maxlen=history)
    for line in lines:
        line_num += 1
        if pattern in line:
            yield line_num, line, previous_lines
        previous_lines.append(line)


def print_usage(my_name):
    print '''Usage:
    %s keyword file.txt
    %s -h
    %s --help
    ''' % (my_name, my_name, my_name)


def is_valid(flag):
    if isinstance(flag, bool):
        return flag == True
    elif isinstance(flag, int):
        return flag != 0
    elif flag:
        return flag is not None
    else:
        return False


def check_filename_and_keyword(filename, sentence):
    if not os.path.exists(filename) or not os.access(filename, os.W_OK):
        return False
    if not sentence or not isinstance(sentence, str) or len(sentence) == 0:
        return False
    return True


def grep_keyword_from_file(tofind, filename, history):
    my_dict = OrderedDict()
    with open(input_file) as f:
        for line_num, line, previous_line in search(f, tofind, history):
            line_start = line_num - len(previous_line)
            for pline in previous_line:
                my_dict[line_start] = pline
                # print line_start, "\t", pline,
                line_start += 1
            #print line_num , "\t", line,
            my_dict[line_num] = line
    return my_dict


if __name__ == '__main__':
    if len(argv) != 3:
        print_usage(argv[0])
        exit(0)
    keyword, input_file = argv[1:3]
    if not is_valid(check_filename_and_keyword(input_file, keyword)):
        exit(1)
    result = grep_keyword_from_file(keyword, input_file, 3)
    previous_line_number = 0
    for line_num, line in result.iteritems():
        if line_num > previous_line_number + 1:
            print '... '
        print '%03d' % line_num, '\t', line,
        previous_line_number = line_num
