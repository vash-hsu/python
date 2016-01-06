
from hashlib import sha1
import datetime
import time

RFC_NewLine = '\r\n'
Default_Banner = 'SmtpUtil Simple Mail Transfer Service'
Default_FQDN = "mail.example.com"


def uuid(input_buffer):
    target = sha1()
    if isinstance(input_buffer, list):
        for i in input_buffer:
            target.update(i)
    else:
        target.update(input_buffer)
    return_uuid = target.hexdigest()
    return return_uuid


def timestamp():
    t = time.time()
    return datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')


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

    @property
    def body(self):
        return self.msg

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
        if len(self.msg) > 0:
            return 1
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
