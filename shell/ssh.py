#!/usr/bin/env python

import paramiko
import getopt
import sys
import getpass
import socket


CONST_DEFAULT_BUFFER_SIZE = 1024
CONST_SSH_PORT = 22
CONST_SSH_DEFAULT_TIMEOUT = 10

def usage_help():
    print '''Usage: [USERNAME@]IP [-p PORT] [--password PASSWORD] [command line]
    -p        : port number, default is 22
    --password: password (not recommended)
Example:
    127.0.0.l
    -p 22 127.0.0.1
    -p 22 --password password user@127.0.0.1 "hostname & whoami & last"
    '''


class Profile:
    def __init__(self, name, passcode, ipv4, portnum, cli):
        self.id = name
        self.pwd = passcode
        self.ip = ipv4
        self.prt = portnum
        self.cli = cli

    def debug(self):
        print "(name, password, ipaddress, port, commandline) = ", \
            self.id, self.pwd, self.ip, self.prt, self.cli

    @property
    def name(self):
        return self.id

    @property
    def password(self):
        return self.pwd

    @property
    def ipaddress(self):
        return self.ip

    @property
    def port(self):
        return self.prt

    @property
    def commandline(self):
        return self.cli


def is_valid_ipv4(string):
    ''''
    >>> is_valid_ipv4('127.0.0.1')
    True

    >>> is_valid_ipv4('192.168.1.1')
    True

    >>> is_valid_ipv4('255.255.255')
    False
    '''
    # http://stackoverflow.com/questions/319279/
    # how-to-validate-ip-address-in-python
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


def parse_str_to_username_ipaddr(string):
    ''''
    >>> parse_str_to_username_ipaddr('127.0.0.1')
    (None, '127.0.0.1')

    >>> parse_str_to_username_ipaddr('root@192.168.1.1')
    ('root', '192.168.1.1')

    >>> parse_str_to_username_ipaddr('255.255.255')
    (None, None)
    '''
    if not string or len(string) < 7:
        return None, None
    position = string.rfind('@')
    name = None
    ip = None
    if position > 0:
        name = string[0:position]
        ip = string[position+1:]
        if is_valid_ipv4(ip):
            return name, ip
    else:
        ip = string if is_valid_ipv4(string) else None
    return name, ip


def parse_parameter(list_para):
    username = None
    password = None
    ipaddress = None
    port = CONST_SSH_PORT
    command = None
    try:
        opts, args = getopt.getopt(list_para, 'hp:', ['help', 'password='])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                return None
            elif opt == '-p':
                port = int(arg) if arg.isdigit() else CONST_SSH_PORT
            elif opt == '--password':
                password = arg
        for term in args:
            if not ipaddress:
                str_name, str_ip = parse_str_to_username_ipaddr(term)
                if str_name:
                    username = str_name
                if str_ip:
                    ipaddress = str_ip
                else:
                    print "ERROR: not valid IPv4 address:", str_ip
                    return None
            else:
                if len(term) > 0:
                    command = term
    except getopt.GetoptError as err:
        print str(err)
        return None
    return Profile(name=username, passcode=password,
                  ipv4=ipaddress, portnum=port, cli=command)


def my_ssh_helper(ini):
    #ini.debug()
    client = paramiko.SSHClient()
    # force username:password only
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    username = ini.id if ini.id else getpass.getuser()
    password = ini.password if ini.password else getpass.getpass()
    # connect
    client.connect(ini.ip, port=ini.port, username=username, password=password,
                   timeout=CONST_SSH_DEFAULT_TIMEOUT,  # timeout for TCP connect
                   allow_agent=True,
                   look_for_keys=False,  # disable searching for ~/.ssh/
                   )
    if ini.cli and len(ini.cli) > 0:
        ssh_session = client.get_transport().open_session()
        if ssh_session.active:
            ssh_session.exec_command(ini.cli)
            while True:
                rawdata = ssh_session.recv(CONST_DEFAULT_BUFFER_SIZE)
                if not rawdata or len(rawdata) == 0:
                    break
                print rawdata
    else:  # file a shell
        ssh_session = client.get_transport().open_session()
        if ssh_session.active:
            ssh_session.exec_command('hostname')
            hostname = ssh_session.recv(CONST_DEFAULT_BUFFER_SIZE).rstrip()
            print "DEBUG: hostname =", hostname
        mytransport = client.get_transport()
        username = mytransport.get_username()
        while True:
            try:
                userinput = raw_input("%s@%s# " % (username, hostname))
            except KeyboardInterrupt:
                print "\n\n<INFO> user interrupt by Ctrl + C"
                break
            if userinput == 'exit':
                break
            ssh_session = client.get_transport().open_session()
            ssh_session.exec_command(userinput)
            print ssh_session.recv(CONST_DEFAULT_BUFFER_SIZE).rstrip()
        client.close()
    return

if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        usage_help()
        sys.exit(0)
    profile = parse_parameter(sys.argv[1:])
    if profile:
        try:
            my_ssh_helper(profile)
        except KeyboardInterrupt:
            print "\n\n<INFO> user interrupt by Ctrl + C"
        except paramiko.AuthenticationException as err:
            print "ERROR: Authentication Failure"
            print str(err)
        except paramiko.SSHException as err:
            print "ERROR: SSH Failure"
            print str(err)
        except socket.error as err:
            print "ERROR: Common Network Failure"
            print str(err)
    else:
        print "Oops!"
