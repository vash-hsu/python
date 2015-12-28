## Test Server for DNS Protocol/Environment ##
-----
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
 + .
 + CASE: UtilityTest.testExample
 + DESC: -p 10053 -f 8.8.8.8:53
 + .
 + CASE: UtilityTest.testNotSupportDomainName
 + DESC: -p 10053 -f google-public-dns-a.google.com:53
 + .
 + CASE: UtilityTest.testNotSupportIPv6
 + DESC: -p 10053 -f fe80::a838:bed2:7ef8:5950:53
 + .
 + CASE: UtilityTest.testNothing
 + DESC: no parameters specified
 + .
 + CASE: UtilityTest.testPrivateIP
 + DESC: -p 10053 -f 192.168.1.1:53
 + .
 + CASE: UtilityTest.testUserError
 + DESC: -p 10053 -f 192.168.1.153
 + DESC: -p 99999 -f 192.168.1.1:53
 + .
 + ----------------------------------------------------------------------
 + Ran 7 tests in 0.020s
 +
 + OK


#### coverage ####
- **python -m coverage run --branch -a test_dns_forward_server.py
- **python -m coverage run --branch -a dns_forward_server.py -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -f 192.168.100.100:53**
 - **python -m coverage report** 
 + 
 + Name                         Stmts   Miss Branch BrPart  Cover
 + --------------------------------------------------------------
 + dns_forward_server.py          189     34     52      6    80%
 + test_dns_forward_server.py      69      4      2      1    93%
 + --------------------------------------------------------------
 + TOTAL                          258     38     54      7    83%
- **python -m coverage html**
 + dns_forward_server_py-0c0f68f.png


####unittest: test_dns_forward_server.py####
- **test_dns_forward_server.py**


####end-to-end RAT test####
- **test command for server**
 + dns_forward_server.py -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -f 192.168.100.100:53
 - or
 + dns_forward_server_verbose.py -p 53 -f 8.8.8.8:53 -f 168.95.1.1:53 -f 192.168.100.100:53 --verbose
- **test command for client on Windows**
 + for /l %x in (1, 1, 10) do nslookup www.google.com 127.0.0.1
