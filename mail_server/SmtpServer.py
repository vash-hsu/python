#!/usr/bin/env python

import inspect
import threading
import SocketServer
import os
from SmtpUtil import SMTPUtil, RFC_NewLine


'''
SMTP 127.0.0.1:25
'''


def whoami():
    func_name = inspect.stack()[1][3]
    return str("%s" % func_name)


# http://stackoverflow.com/questions/6810999/
# how-to-determine-file-function-and-line-number
def debug_helper(message, level=2):
    caller_frame_record = inspect.stack()[1+level]
    frame = caller_frame_record[0]
    info = inspect.getframeinfo(frame)
    return "DEBUG: %s ... %s@%s(%d)" % (message, info.function,
                                 os.path.split(info.filename)[-1],
                                 info.lineno)


def logger(message, level='INFO'):
    print "%s: %s" % (level, message)


def debugger(message):
    print debug_helper(message, level=1)


class Profile:

    def __init__(self):
        self.config = dict()
        self.config['threshold'] = 0
        self.config['logger'] = None
        self.config['debug'] = None
        self.config['ip'] = '127.0.0.1'
        self.config['port'] = 25

    def setup(self, name, value):
        if name in self.config:
            self.config[name] = value
            return True
        return False

    def dump(self):
        for i in self.config:
            print "[%s] " % i,
        print

    @property
    def threshold(self):
        return self.config[whoami()]

    @property
    def logger(self):
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


class ThreadedSMTPServer(SocketServer.ThreadingMixIn,
                         SocketServer.TCPServer):

    def __init__(self, server_address, handler):
        self._profile = None
        self.cb_mailbody = None
        SocketServer.TCPServer.__init__(self,
                                        server_address,
                                        RequestHandlerClass=handler)

    def set_callback_mailbody(self, callback):
        self.cb_mailbody = callback

    def get_callback_mailbody(self):
        return self.cb_mailbody

    def set_profile(self, profile):
        self._profile = profile

    @property
    def profile(self):
        return self._profile


class ThreadedSMTPHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        smtpu = SMTPUtil(self.server.profile.logger,
                         self.rfile.readline,
                         self.request.sendall)
        smtpu.banner()
        while True:
            data_recv = self.rfile.readline()
            dataset = data_recv.strip(RFC_NewLine).split(' ')
            if len(dataset) == 0 or len(dataset[0]) == 0:  # ?
                continue
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
            if is_continue > 0:
                if self.server.profile and self.server.profile.debug:
                    self.server.profile.debug('=== content from DATA ===')
                    self.server.profile.debug(repr(smtpu.body))
                body_handler = self.server.get_callback_mailbody()
                if body_handler:
                    body_handler(to_address=smtpu.recp_to, message=smtpu.body)
                smtpu.fresh()


def host_smtpd(profile, cb_mailbody=None):
    server = ThreadedSMTPServer((profile.ip, profile.port),
                                ThreadedSMTPHandler)
    server.set_profile(profile)
    if cb_mailbody:
        server.set_callback_mailbody(cb_mailbody)
    if profile.logger:
        profile.logger("hosting at %s" % str(server.server_address))
        profile.logger("type exit or quit to terminate this service")
    #
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    # when stop condition meet
    try:
        while raw_input().lower() not in ('exit', 'quit'):
            continue
    except KeyboardInterrupt:
        if profile.debug:
            profile.debug("User Interrupt by Ctrl + C")
    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    configuration = Profile()
    configuration.setup('logger', logger)
    # configuration.setup('debug', debugger)
    host_smtpd(configuration)
