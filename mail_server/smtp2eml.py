#!/usr/bin/env python
# ---------- ---------- ---------- ---------- ----------
# 2016/01/04 @ Vash Hsu, porting from Perl to Python
#
# Purpose
#    Outlook --> SMTP 127.0.0.1 --> 10025 port listened by SMTP2LocalEML
#    --> create folder under working directory
#    --> save raw mail from SMTP protocol in name/form of
#   (to do)
#        YearMonthDay-HourMinuteSecond.eml
#    --> save attached RFC822
#        into YearMonthDay-HourMinuteSecond\00000001.eml
#        into YearMonthDay-HourMinuteSecond\00000002.eml
# ---------- ---------- ---------- ---------- ----------

import inspect
import threading
import SocketServer
import os, sys
from hashlib import sha1

Version = '20160103-v0.2'
Default_Buffer_Size = 1024
RFC_NewLine = '\r\n'
Default_Banner = 'SMTP2EML Simple Mail Transfer Service'
Default_FQDN = "mail.example.com"
Default_MailStore = ".mailstore"
MailStorePath = Default_MailStore


def whereami():
    icu = inspect.currentframe()
    funcname = inspect.stack()[1][3]
    return str("%s(%d)" % (funcname, icu.f_back.f_lineno))


# http://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
def whocallme(level=2):
    callerframerecord = inspect.stack()[1+level]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return "%s@%s(%d)" % (info.function,
                          os.path.split(info.filename)[-1],
                          info.lineno)


def whoami():
    icu = inspect.currentframe()
    funcname = inspect.stack()[1][3]
    return str("%s" % funcname)


def debug_helper(message, level=2):
    print "DEBUG: %s ... (%s)" % (message, whocallme(level))


class Profile:

    def __init__(self):
        self.config = dict()
        self.config['threshold'] = 0
        self.config['debug'] = None
        self.config['ip'] = '0.0.0.0'
        self.config['port'] = 10025
        self.config['folder'] = '.mailstore'

    def setup(self, name, value):
        if name in self.config:
            self.config[name] = value

    def dump(self):
        for i in self.config:
            print "[%s] " % i,
        print

    @property
    def threshold(self):
        return self.config[whoami()]

    @property
    def debug(self):
        return self.config[whoami()]

    @property
    def ip(self):
        return self.config[whoami()]

    @property
    def port(self):
        return self.config[whoami()]

    @property
    def folder(self):
        return self.config[whoami()]


class SMTPUtil:
    def __init__(self, logger=None, reader=None, writer=None):
        self.commands = [
            'data',
            'helo',
            'ehlo',
            'help',
            'mail',
            'noop',
            'quit',
            'rcpt',
            'reset',
            'vrfy'
        ]
        self.reader = reader
        self.writer = writer
        self.recp_to = []
        self.mail_from = ''
        self.msg = ''
        self.logger = logger

    def _reset(self):
        self.recp_to = []
        self.mail_from = ''
        self.msg = ''

    def fresh(self):
        self._reset()

    def _content_helper(self):
        if not self.reader:
            pass
        while True:
            linein = self.reader()
            if linein == '.' + RFC_NewLine:
                break
            yield str(linein)

    # append RFP_NewLine
    def write(self, data):
        if self.writer:
            self.writer(data + RFC_NewLine)
        if self.logger:
            self.logger("Server Response: " + data)

    def banner(self, string_fqdn=None, string_banner=None,
               specified_writer=None):
        if not string_fqdn:
            string_fqdn = Default_FQDN
        if not string_banner:
            string_banner = Default_Banner
        response = " ".join(['220', string_fqdn, string_banner])
        if specified_writer:
            specified_writer(response + RFC_NewLine)
        if self.writer:
            self.write(response)
        else:
            return response
        return ''

    def command(self, name, reader=None, writer=None):
        candidate = name.strip().lower()
        if candidate in self.commands:
            self.reader = reader
            self.writer = writer
            return getattr(self, candidate)
        else:
            return None

    def data(self, params):
        if len(self.recp_to) == 0 or len(self.mail_from) == 0:
            self.write("503 bad sequence of commands")
            return -1
        self.write("354 Start mail input; end with <CRLF>.<CRLF>")
        rawdata = ''
        try:
            for i in self._content_helper():
                rawdata += i
        except BaseException as err:
            print ("ERRRO:", str(err))
            self.write("550 Requested action not taken")
            return -1
        # RFC_NewLine + '..' --> RFC_NewLine + '.'
        self.msg = rawdata.replace(RFC_NewLine + '..', RFC_NewLine + '.')
        self.write("250 OK")
        return 0

    def helo(self, params):
        guest = ' '.join(params) if params else 'Nobody'
        print "INFO:", "client came from " + guest
        self.write("250 Hello " + ' '.join(params))
        return 0

    def ehlo(self,  params):
        self.write("502 Command not implemented")
        return 0

    def help(self, params):
        self.write('211 ' + " ".join(self.commands))
        return 0

    def mail(self, params):
        ''''
            mail from: user@hello.world.com
            mail from:<user@hello.world.com>
            '''
        user_specified_address = None
        if params:
            if len(params) >= 2 and params[0].lower() == 'from:':
                sender_address = params[1].strip()
                if len(sender_address) > 0:
                    user_specified_address = sender_address
            elif len(params) == 1 and 'from:' in params[0].lower():
                offset = params[0].lower().find('from:')
                if offset >= 0:
                    sender_address = params[0][offset+len('from:'):].strip()
                    if len(sender_address) > 0:
                        user_specified_address = sender_address
        if user_specified_address:
            self.mail_from = user_specified_address
            self.write("250 OK for user %s" % self.mail_from)
            return 0
        self.write("501 Syntax error")
        return 0

    def noop(self, params):
        self.write("250 OK")
        return 0

    def quit(self, params):
        self.write("221 Goodbye")
        return -1

    def rcpt(self, params):
        user_specified_address = None
        if params:
            if len(params) >= 2 and params[0].lower() == 'to:':
                user_address = params[1].strip()
                if len(user_address) > 0:
                    user_specified_address = user_address
            elif len(params) == 1 and 'to:' in params[0].lower():
                offset = params[0].lower().find('to:')
                if offset >= 0:
                    user_address = params[0][offset+len('to:'):].strip()
                    if len(user_address) > 0:
                        user_specified_address = user_address
        if user_specified_address:
            self.recp_to.append(user_specified_address)
            self.write("250 OK its for %s" % user_specified_address)
            return 0
        self.write("501 Syntax error")
        return 0

    def reset(self, params):
        self._reset()
        self.write("250 OK")
        return 0

    def vrfy(self, params):
        self.write('502 Command not implemented')
        return 0


# class ThreadedSMTPHandler(SocketServer.BaseRequestHandler):
class ThreadedSMTPHandler(SocketServer.StreamRequestHandler):

    def write_maildata_to_local_eml_file(self, folder_path, to_address,
                                         message):
        target = sha1()
        target.update(message)
        message_id = target.hexdigest()
        for i in to_address:
            # security issue if address give us surprise
            target = sha1()
            target.update(i.lower())
            base_path = os.path.join(folder_path, target.hexdigest())
            debug_helper("%s = %s" % (repr(i), base_path))
            try:
                if not os.path.exists(base_path):
                    os.makedirs(base_path)
                if os.path.isdir(base_path):
                    eml_path = os.path.join(base_path, message_id + '.eml')
                    with open(eml_path, 'wb') as writer:
                        writer.write(message)
                else:
                    debug_helper("Fail to dump eml on specific folder name %s" %
                                 base_path)
            except BaseException as err:
                debug_helper("Exception: %s" % str(err))

    def handle(self):
        # process
        cur_thread = threading.current_thread()
        dmg = "{}: {}".format(cur_thread.name, str(self.client_address))
        print "DEBUG:", dmg
        smtpu = SMTPUtil(debug_helper,
                         self.rfile.readline, self.request.sendall)
        smtpu.banner()
        # process
        while True:
            # data_recv = self.request.recv(Default_Buffer_Size)
            #  ... readline() instead of raw recv()
            data_recv = self.rfile.readline()
            dataset = data_recv.strip(RFC_NewLine).split(' ')
            if len(dataset) == 0 or len(dataset[0]) == 0:
                debug_helper('Empty Input, skip and go to next loop')
                continue
            debug_helper(data_recv, level=1)
            fptr = smtpu.command(dataset[0].lower(),
                                 self.rfile.readline,
                                 self.request.sendall)
            if fptr:
                parameter = None if len(dataset) == 1 else dataset[1:]
                is_continue = fptr(parameter)
            else:
                self.request.sendall("501 " + "Syntax error" + RFC_NewLine)
                is_continue = 0
            if is_continue < 0:
                break
            # if it is necessary to write out msg
            if len(smtpu.msg) > 0:
                self.write_maildata_to_local_eml_file(MailStorePath,
                                                      smtpu.recp_to, smtpu.msg)
                smtpu.fresh()


class ThreadedSMTPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def hosting_a_smtp_server(profile):
    # setting server socket
    HOST, PORT = profile.ip, profile.port
    server = ThreadedSMTPServer((HOST, PORT), ThreadedSMTPHandler)
    print "INFO: hosting at", server.server_address
    print "INFO: type exit or quit to terminate this service ..."
    #
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    # when stop condition meet
    try:
        while raw_input().lower() not in ('exit', 'quit'):
            continue
    except KeyboardInterrupt:
        print "INFO: User Interrupt by Ctrl + C"
    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    # configuration
    configuration = Profile()
    if os.path.exists(configuration.folder):
        if not os.path.isdir(configuration.folder):
            print "ERROR: %s should not be file" % configuration.folder
            sys.exit(-1)
    else:
        try:
            os.makedirs(configuration.folder)
        except BaseException as err:
            print "ERROR: %s" % str(err)
            sys.exit(-2)
    MailStorePath = configuration.folder
    hosting_a_smtp_server(configuration)
