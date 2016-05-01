#!/usr/bin/env python

VERSION = '0.1'

import os
import csv
import sys

# input
#  name_list with option mapping (original input)
#     basic checking: there should be at most 1 unique ID mapping one option
#                   : redundant IDs will be purged in form of (ID, option)
#  name with lower priority (gray list)
#  name with lowest priority (blacklist)
#  name with zero priority (denylist)

# |---------|---------|---------|
#   BLACK    GRAY       CAUSAL
# | 0                        10 |
# | sad                   happy |
# |---------|---------|---------|
WHO_IN_BLACKLIST_RANDOM_STRAT = -1
WHO_IN_BLACKLIST_RANDOM_STOP  = 0
WHO_IN_GRAYLIST_RANDOM_STRAT  = 1
WHO_IN_GRAYLIST_RANDOM_STOP   = 10
WHO_IN_CAUSAL_RANDOM_STRAT    = 10
WHO_IN_CAUSAL_RANDOM_STOP     = 100


def print_usage():
    print "Usage: --if input.csv --of output.csv"
    print "       --gray <DIR_GRAYLIST>"
    print "       --black <BLACK_BLACKLIST>"
    print "       --deny <DIR_DENYLIST>"


def get_parameters(params):
    import getopt
    try:
        opts, args = getopt.getopt(params, "hvi:o:g:b:d:",
                                   ["help", "version", "ver",
                                    "if=", "of=", "gray=", "black=", "deny="])
    except getopt.GetoptError as err:
        print str(err)
        return None
    ready = dict()
    for o, a in opts:
        if o in ("-v", "--version", "--ver"):
            ready['version'] = True
        elif o in ("-h", "help"):
            ready['help'] = True
        elif o in ("-i", "--if"):
            ready['input'] = a
        elif o in ("-o", "--of"):
            ready['output'] = a
        elif o in ("-g", "--gray"):
            ready['gray'] = a
        elif o in ("-b", "--black"):
            ready['black'] = a
        elif o in ("-d", "--deny"):
            ready['deny'] = a
        else:
            return None
    return ready


def is_stringascii(instring):
    try:
        instring.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def convert_dbcs_to_unicode(instring):
    try:
        decoded = instring.decode('big5')
        encoded = decoded.encode('utf8')
        return encoded
    except (UnicodeDecodeError, UnicodeEncodeError):
        return ""


def cook_input_csv(filename):
    raw_data = []
    with open(filename, 'rt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        for row in csv_reader:
            if len(row) == 3:
                _id, _date, _option = row
                if not is_stringascii(_id): # skip header, dirty logic
                    print "SKIP:", str(row)
                    continue
                _id.strip()
                #_option = convert_dbcs_to_unicode(_option)
                raw_data.append((_id, _option))
            else:
                print "EXCEPTION:", row
    return raw_data


def generate_new_filename(filename):
    return filename


def retrieve_namelist_from_file(filename):
    namelist = []
    with open(filename, "r") as reader:
        for i in reader:
            name_string = i[:i.find('(')].strip()
            namelist.append(name_string)
    return namelist


def retrieve_namelist_from(target_path):
    if not os.path.exists(target_path):
        return []
    if os.path.isfile(target_path):
        return retrieve_namelist_from_file()
    if os.path.isdir(target_path):
        namelist = []
        for child_file in os.listdir(target_path):
            file_path = os.path.join(target_path,child_file)
            namelist.extend(retrieve_namelist_from_file(file_path))
        return namelist
    print "EXCEPTION: oops, is there anything going wrong?"
    return []


def preprocess_config(raw_config):
    cooked = dict()
    if 'input' in raw_config and os.path.exists(raw_config['input']):
        cooked['input'] = cook_input_csv(raw_config['input'])
    if 'output' in raw_config and not os.path.isdir(raw_config['output']):
        cooked['output'] = generate_new_filename(raw_config['output'])
    for target in ('gray', 'black', 'deny'):
        if target in raw_config and os.path.exists(raw_config[target]):
            cooked[target] = retrieve_namelist_from(raw_config[target])
    return cooked


def remove_denied_from_list(source, denied):
    purified = dict()
    for who, what in source:
        if who not in denied:
            # purified.append((who, what))
            purified[who] = what
        else:
            print "DENY: removing [%s]" % who
    return purified


def give_random_position_by_order(mixed, gray, black):
    import random
    random_positions = dict()
    for somebody in mixed:
        position = 0
        if somebody in black:
            position = random.uniform(WHO_IN_BLACKLIST_RANDOM_STRAT,
                                      WHO_IN_BLACKLIST_RANDOM_STOP)
        elif somebody in gray:
            position = random.uniform(WHO_IN_GRAYLIST_RANDOM_STRAT,
                                      WHO_IN_GRAYLIST_RANDOM_STOP)
        else:
            position = random.uniform(WHO_IN_CAUSAL_RANDOM_STRAT,
                                      WHO_IN_CAUSAL_RANDOM_STOP)
        random_positions[somebody] = position
    return random_positions


def lottery(dict_input):
    report_dict = dict()
    for i in ('input', 'gray', 'black', 'deny'):
        print "%s(%d);" % (i, len(dict_input[i])),
    print
    # business logic, rule #1: nobody in deny list
    if 'deny' in dict_input and len(dict_input['deny']) > 0:
        who_with_what = remove_denied_from_list(dict_input['input'],
                                                dict_input['deny'])
    else:
        who_with_what = dict()
        for who, what in dict_input['input']:
            who_with_what[who] = what
    # business logic, rule #2: causal > gray > black
    who_with_priority = give_random_position_by_order(who_with_what,
                                                      dict_input['gray'],
                                                      dict_input['black'])
    # business logic, rule #3: who with priority group by what
    for who in who_with_what:
        priority = who_with_priority[who]
        what = who_with_what[who]
        if what not in report_dict:
            report_dict[what] = list([(who, priority), ])
        else:
            report_dict[what].append((who, priority))
    return report_dict


def write_to_csv(raw_report, filename):
    output_file = []
    file2write_counter = 0
    for i in raw_report:
        print "%s #(%d)" % (i, len(raw_report[i]))
        file2write_counter += 1
        file2write = ".".join([filename, '%d' % file2write_counter, 'csv'])
        output_file.append("%s: %s" % (file2write, i))
        with open(file2write, 'wb') as csvfile:
            writer = csv.writer(csvfile,
                                delimiter=',', quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
            for _who, _priority in raw_report[i]:
                writer.writerow([str(_who), str(_priority)])
    return output_file


if __name__ == '__main__':
    raw_config = get_parameters(sys.argv[1:])
    if not raw_config or len(raw_config) == 0:
        print_usage()
        sys.exit(-1)
    if 'version' in raw_config:
        print "Version: %s" % str(VERSION)
    if 'help' in raw_config:
        print_usage()
        sys.exit(0)
    # business logic
    good = preprocess_config(raw_config)
    candidate_list = lottery(good)
    result = write_to_csv(candidate_list, good['output'])
    # telling what's next
    for i in result:
        print i
