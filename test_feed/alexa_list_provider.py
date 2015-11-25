#!/usr/bin/env python

import sys
import os
import dns.resolver
import time
import requests


alexa_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
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
def nslookup(target, type):
    latency = time.clock()
    answer = None
    myresolver = dns.resolver.Resolver()
    # to wait for a response from a server, before timing out.
    myresolver.timeout = CONST_DNS_TIMEOUT
    # to get an answer to the question.
    myresolver.lefttime = CONST_DNS_TIMEOUT + 2
    try:
        queried = myresolver.query(target, type)
        answer = str(queried.response.answer[0].items[0])
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        answer = 'NXDOMAIN'
    except (dns.resolver.Timeout,
            dns.resolver.YXDOMAIN, dns.resolver.NoNameservers):
        pass
    finally:
        latency = time.clock() - latency
        return answer, round(latency, 3)


def nslookup_with_retry(target, type, retry):
    fail_count = 0
    answer = 'N/A'
    latency = 0
    while fail_count <= retry:
        fail_count += 1
        rA, latency = nslookup(target, type)
        if rA is not None:
            answer = rA
            break
    return answer, str(latency)


def download_alexa_zip():
    pass


def is_valid_ipv4(string):
    import socket
    try:
        socket.inet_pton(socket.AF_INET, string)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(string)
        except socket.error:
            return False
        return string.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True


def httping(target):
    latency = time.clock()
    response = requests.head("http://"+target, allow_redirects=True)
    latency = round(time.clock() - latency, 3)
    legacy = [str(i.status_code) for i in response.history]
    if 200 <= int(response.status_code) < 300:
        return str(response.status_code), latency, legacy + [str(response.status_code)]
    else:
        return None, latency, legacy + [str(response.status_code)]


def httping_with_retry(target, retry):
    fail_count = 0
    answer = 'N/A'
    latency = 0
    history = []
    while fail_count <= retry:
        fail_count += 1
        rA, latency, history = httping(target)
        if rA is not None:
            answer = rA
            break
    return answer, str(latency), history


def get_dns_httping_result(target):
    data = list()
    answer, latency = nslookup_with_retry(target, 'A', CONST_RETRY)
    data.append(answer)
    data.append(latency)
    if is_valid_ipv4(answer):
        answer, latency, history = httping_with_retry(target, CONST_RETRY)
        data.append(answer)
        data.append(latency)
        if len(history):
            data.append(';'.join(history))
    return data


def alexa_go_go_go(top_many):
    # download top-1m.csv.zip
    # unzip top-1m.csv
    print ','.join(['rank', 'domain', 'nslookup', 'secs', 'httping', 'secs', 'notes'])
    counter = 0
    with open("top-1m.csv", 'r') as reader:
        for line in reader:
            counter += 1
            sn, domain = line.rstrip().split(',')
            reputation = get_dns_httping_result(domain)
            print ','.join([sn, domain] + reputation)
            if counter >= top_many:
                break


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1 \
            or '-h' in sys.argv[1:] \
            or '--help' in sys.argv[1:]:
        print_usage(os.path.split(sys.argv[0])[-1])
        sys.exit(0)
    if sys.argv[1].isdigit():
        alexa_go_go_go(int(sys.argv[1]))
    else:
        print "ERROR: %s is not numeric" % sys.argv[1]
