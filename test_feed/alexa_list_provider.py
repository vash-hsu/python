#!/usr/bin/env python

import sys
import os
import dns.resolver
import time
import requests
from datetime import datetime


alexa_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
alexa_zip = 'top-1m.csv.zip'
alexa_csv = 'top-1m.csv'
CONST_DNS_TIMEOUT = 2
CONST_HTTP_TIMEOUT = 10
CONST_HTTPS_TIMEOUT = 15
CONST_RETRY = 1


def print_usage(myself):
    print """Usage: %s NUMBER
Example
    %s 10
    %s 100 > alexa.csv
    """ % (myself, myself, myself)


# answer, latency
def nslookup(target, type='A', retry=0):
    yesterday = time.clock()
    iplist = list()
    answer = 'N/A'
    myresolver = dns.resolver.Resolver()
    myresolver.timeout = CONST_DNS_TIMEOUT
    myresolver.lefttime = CONST_DNS_TIMEOUT
    try:
        queried = myresolver.query(target, type)
        for response in queried.response.answer:
            if response.rdtype == 1:  # A
                for j in response:
                    iplist.append(j.to_text())
    except BaseException:
        pass
    if len(iplist) > 0:
        answer = ';'.join(iplist)
    elif retry > 0:
        result = nslookup(target, type, retry-1)
        answer = result[0]
    today = time.clock()
    latency = today - yesterday
    return [answer, str(round(latency, 3))]


def download(target_url, filename):
    r = requests.get(target_url, stream=True)
    try:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except BaseException as err:
        print "ERROR:", str(err)
        return False
    return True


def unzip(input_zip, target_file):
    print "TODO: unzip %s from %s" % (target_file, input())
    return False


def httping(target, retry=0):
    yesterday = time.clock()
    rcode = '0'
    story = ''
    try:
        response = requests.head(target,
                                 allow_redirects=True,
                                 timeout=2.0)
        rcode = str(response.status_code)
        legacy = [str(i.status_code) for i in response.history]
        story = ';'.join(legacy + [str(response.status_code)])
    except KeyboardInterrupt as err:
        print "WARNING: User Cancel by Ctrl+C"
        today = time.clock()
        latency = str(round(today - yesterday, 3))
        return ['-99', latency, '']
    except BaseException as err:
        print "WARNING:", err.__class__.__name__
        print "Exception:", str(err)
    finally:
        if 200 <= int(rcode) < 300:
            today = time.clock()
            latency = str(round(today - yesterday, 3))
            return [rcode, latency, story]
    # retry?
    if retry > 0:
        children = httping(target, retry-1)
        today = time.clock()
        latency = str(round(today - yesterday, 3))
    return [children[0], latency, children[2]]


def get_dns_httping_result(target):
    result = list()
    answer, latency = nslookup(target, 'A', CONST_RETRY)
    result += [answer, latency]
    if answer != 'N/A':
        answer, latency, history = httping('http://' + target,
                                           CONST_RETRY)
        result += [answer, latency, history]
    return result


def pick_up_name(source, middle_name, timestamp):
    return '-'.join([
        os.path.splitext(source)[0],
        middle_name,
        timestamp.strftime("%Y-%m-%d_%H%M")
    ]) + '.csv'


def alexa_go_go(input_file, top_many):
    output_file = pick_up_name(input_file, str(top_many), datetime.now())
    try:
        writer = open(output_file, 'w')
    except BaseException as err:
        print "ERROR: fail to prepare output file", output_file
        print "WARNING:", err.__class__.__name__
        print "Exception: ", str(err)
        return False
    try:
        writer.writelines(','.join(['rank', 'domain', 'ip',
                                    'nslookup(sec)', 'httping',
                                    'httping(secs)', 'notes'])+'\n')
        counter = 0
        with open("top-1m.csv", 'r') as reader:
            for line in reader:
                counter += 1
                sn, domain = line.rstrip().split(',')
                reputation = get_dns_httping_result(domain)
                writer.writelines(','.join([sn, domain] + reputation)+'\n')
                if counter >= top_many:
                    break
    except KeyboardInterrupt as err:
        print "WARNING: User Cancel by Ctrl+C"
    except BaseException as err:
        print "ERROR: fail to prepare output file", output_file
        print "WARNING:", err.__class__.__name__
        print "Exception: ", str(err)
    finally:
        writer.close()


def alexa_go(top_many):
    # download top-1m.csv.zip
    if not os.path.isfile(alexa_zip):
        if not download(alexa_url, alexa_zip):
            print "ERROR: fail to get the latest %s from %s" %\
                  (alexa_zip, alexa_url)
            return False
    # unzip top-1m.csv
    if not os.path.isfile(alexa_csv):
        if not unzip(alexa_zip. alexa_csv):
            print "ERROR: fail to get latest %s from %s" %\
                  (alexa_csv, alexa_zip)
            return False
    # processing
    return alexa_go_go(alexa_csv, top_many)


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1 \
            or '-h' in sys.argv[1:] \
            or '--help' in sys.argv[1:]:
        print_usage(os.path.split(sys.argv[0])[-1])
        sys.exit(0)
    if sys.argv[1].isdigit():
        if not alexa_go(int(sys.argv[1])):
            sys.exit(-1)
    else:
        print "ERROR: %s is not numeric" % sys.argv[1]
