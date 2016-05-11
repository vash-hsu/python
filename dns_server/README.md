## Test Server for DNS Protocol/Environment ##
-----

### Man in the Middle DNS Server ###
- **dns_mitm_server.py**

#### dns_mitm_server.py -h ####
- **Usage**
 + Usage: -p <PORT>  -f IPv4:PORT  [--verbose]  [-h]
 +  -p PORT      : i.e. 10053 (root is necessary if port < 1024)
 +  -f IPv4:PORT : i.e. 8.8.8.8:53
 +  -a FQDN:IPv4 : i.e. google.com.:127.0.0.1 (NXDOMAIN return without IPv4)
 +  --aaaa FQDN:IPv6 : i.e. google.com.:::1 (NXDOMAIN return without IPv6)
 +  -h           : show help
 + Example:
 +     -p 53 -f 8.8.8.8:53
 +     -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53
 +     -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -a google.com:127.0.0.1
 +     -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -a nxdomain.com.:
 +     -p 53 -f 168.95.1.1:53 --aaaa google.com.:::1 --aaaa nxdomain.com.:


### Forward DNS Server ###
- **dns_forward_server.py**
 + redirect dns request/response between client and backend servers


#### dns_forward_server.py -h ####
- **Usage**
 + Usage: -p <PORT>  -f IPv4:PORT  [-h]
 +   -p PORT      : i.e. 10053 (root is necessary if port < 1024)
 +   -f IPv4:PORT : i.e. 8.8.8.8:53
 +   -h           : show help
 + Example:
 +   -p 10053 -f 8.8.8.8:53
 +   -p 10053 -f 8.8.8.8:53 -f 168.95.1.1:53


#### test_dns_forward_server.py ####
- **test_dns_forward_server.py**
 + ----------------------------------------------------------------------
 + Ran 7 tests in 0.020s
 +
 + OK

#### test_dns_forward_server_verbose.py ####
- **test_dns_forward_server_verbose.py**
 + .
 + CASE: DPITest.testAResponse
 + DESC: Type A Response for google, multiple RR
 + .
 + CASE: DPITest.testAServerFailure
 + DESC: Type A Server Failure
 + WARNING: dnslib.DNSError: Error unpacking DNSQuestion [offset=13]: Not enough by
 + tes [offset=13,remaining=21,requested=46]
 + DESC: there should be no answer returned
 + .
 + ----------------------------------------------------------------------
 + Ran 8 tests in 0.020s
 + 
 + OK

#### coverage ####
- **python -m coverage run --branch -a test_dns_forward_server.py
- **python -m coverage run --branch -a test_dns_forward_server.py
- **python -m coverage run --branch -a dns_forward_server.py -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -f 192.168.100.100:53**
- **python -m coverage report** 
- **python -m coverage html**


####unittest: test_dns_forward_server.py####
- **test_dns_forward_server.py**
- **test_dns_forward_server_verbose.py**


####end-to-end RAT test####
- **test command for server**
 + dns_forward_server.py -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -f 192.168.100.100:53
 - or
 + dns_forward_server_verbose.py -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -f 192.168.100.100:53 --verbose
- **test command for client on Windows**
 + for /l %x in (1, 1, 10) do nslookup www.google.com 127.0.0.1
