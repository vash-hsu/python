#!/usr/bin/env python

import sys
import os
import subprocess
import time
import re
from decimal import Decimal


reg2separate_num_unit = re.compile(r'^([\d\.]+)([GMKgmk%])$')


# return a list with lines, no new line ended
def system_get_stdout(command):
    cmd_list = command.split()
    p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, shell=True)
    data = p.stdout.read()
    candidate = []
    for i in data.rsplit('\r\n'):
        if len(i) > 0:
            candidate.append(i)
    return candidate


def iter_system_get_stdout(command):
    cmd_list = command.split()
    process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, shell=True)
    while True:
        line = process.stdout.readline()
        if line == '':
            break
        else:
            cooked = line.rstrip('\r\n')
            cooked = cooked.rstrip()  # should or should not?
            if len(cooked) > 0:  # discard empty line
                yield cooked
            else:
                continue


def convert_data_unit_to_pure_number(data, unit, unit_to='g', digit=3):
    unit = unit.lower()
    unit_to = unit_to.lower()
    acceptable = ('g', 'm', 'k', '%')
    return_value = float(0)
    # undefined
    if unit not in acceptable:
        return return_value
    # defined
    if unit == unit_to:
        return round(float(data), digit)
    if unit == '%':
        return round(float(data) / 100, digit)
    # one by one
    data = float(data)
    if unit_to == 'g':
        if unit == 'm':
            return_value = round(data/1024, digit)
        elif unit == 'k':
            return_value = round(data/1048576, digit)
    elif unit_to == 'm':
        if unit == 'g':
            return_value = data * 1024
        elif unit == 'k':
            return_value = round(data/1024, digit)
    elif unit_to == 'k':
        if unit == 'g':
            return_value = data * 1048576
        elif unit == 'm':
            return_value = data * 1024
    return return_value


def convert_string_to_pure_number(text, unit_to='g', digit=3):
    if text.isdigit():
        return float(text)
    return_value = float(0)
    # num + unit
    result = reg2separate_num_unit.search(text)
    if result is not None:
        num = result.group(1)
        unit = result.group(2)
        return_value = convert_data_unit_to_pure_number(num, unit, unit_to)
    # num only?
    else:
        result = re.match(r"((\d+)\.(\d+))", text)
        if result is not None:
            return_value = round(float(result.group(1)), digit)
    return return_value


def index_keyword_in_text(keyword, text, sensitive=False):
    keyword2match = keyword if sensitive else keyword.lower()
    text2scan = text if sensitive else text.lower()
    tokens = text2scan.split()
    try:
        return tokens.index(keyword2match)
    except ValueError:
        return -1


# https://docs.python.org/2/library/decimal.html
def convert_exponent(string_in, digit=3):
    d = Decimal(string_in)
    d = d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()
    return str(round(float(d), digit))


# http://fcamel-life.blogspot.tw/2010/11/python.html
# '2010-11-16 20:10:58' -> 1289909458
def convert_string_to_timestamp(text):
    try:
        if text.find('-') > 0:
            return int(time.mktime(time.strptime(text, '%Y-%m-%d %H:%M:%S')))
        elif text.find('/') > 0:
            return int(time.mktime(time.strptime(text, '%Y/%m/%d %H:%M:%S')))
    except ValueError as err:
        sys.stderr.write("ERROR: %s\n" % str(err))
    return int(-1)


# 1289909458 -> '2010-11-16 20:10:58'
def convert_timestamp_to_string(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(timestamp)))
