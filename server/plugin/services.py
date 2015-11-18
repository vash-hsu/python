#!/usr/bin/env python

import time
from calendar import calendar

# twisted
from twisted.web.resource import Resource

from htmlwritter import *
from httpstatuscode import *


class HttpStatusCodeProvider(Resource):
    code = 404

    def __init__(self, code, history=0):
        Resource.__init__(self)
        self.history = history
        if code.isdigit():
            self.code = int(code)

    def getChild(self, path, request):
        if path is not None and path.isdigit():
            self.history = int(path)
        return self

    def render_GET(self, request):
        request.setResponseCode(self.code)
        if self.code in [302, ]:
            self.history += 1
            myhost = str(request.getHeader('Host'))
            myuris = str(request.uri).split('/')
            if self.history > 1:
                myuris = myuris[0:-1]
            redirect_url = 'http://%s%s/%s' \
                           % (myhost, '/'.join(myuris), self.history)
            request.redirect(redirect_url)
        return self.body()

    def body(self):
        if self.code in httpcodeFromWiki:
            if self.history == 0:
                return "<html><body>%d = %s<body></html>" %\
                       (self.code, httpcodeFromWiki[self.code])
            else:
                return "<html><body>%d = %s</br>History = %d<body></html>" %\
                       (self.code, httpcodeFromWiki[self.code], self.history)
        else:
            return "<html><body>%d = undefined http code<body></html>" %\
                   self.code


class Service_ReturnCode(Resource):

    def getChild(self, name, request):
        if name == '' or name == '/' or name == '/index.html':
            return self
        if name.isdigit():
            return HttpStatusCodeProvider(name)
        else:
            return HttpStatusCodeProvider('404')

    def render_GET(self, request):
        content = list()
        content.append(prepare_html_start())
        content.append(prepare_table_start(['Link', 'Description']))
        for i in sorted(httpcodeFromWiki.keys()):
            content.append(prepare_table_raw([
                "<a href=\"%s\">%s</a>" % ('/'.join([request.uri, str(i)]), i),
                httpcodeFromWiki[i]
            ]))
        content.append(prepare_table_stop())
        content.append(prepare_html_stop())
        return '\r\n'.join(content)


class CalendarProvider(Resource):

    def __init__(self, year):
        Resource.__init__(self)
        self.year = year

    def render_GET(self, request):
        return self.body(request)

    def body(self, request):
        # ['', 'calendar']
        # ['', 'calendar', '']
        # ['', 'calendar', '2015']
        # ['', 'calendar', 'abc', '123']
        uris = request.uri.split('/')
        uris = uris[:2]
        uri = '/'.join(uris)
        return "<!DOCTYPE html><html><body><p>" +  \
               "<a href=\"%s/%d\"> &laquo; last year</a>" % (uri, self.year - 1) + \
               "&nbsp;|&nbsp;" + \
               "<a href=\"%s/%d\">next year &raquo; </a>" % (uri, self.year + 1) + \
               "</p><pre>%s</pre></body></html>" % calendar(self.year)


class Service_Calendar(Resource):

    def getChild(self, path, request):
        if path == '' or path == '/' or not path.isdigit():
            return self
        return CalendarProvider(int(path))

    def render_GET(self, request):  # default is this year
        return CalendarProvider(int(time.strftime("%Y", time.gmtime()))).body(request)
