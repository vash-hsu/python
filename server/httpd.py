#!/usr/bin/env python

import getopt
import sys
import os


import plugin.javascript
from plugin.htmlwritter import *
from plugin.services import Service_ReturnCode
from plugin.services import Service_Calendar


# twisted
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
from twisted.web.resource import Resource


def usage_help():
    print '''Usage: [-p PORT] [--folder PUBLIC] [--demo SCRIPTFOLDER]
    -p        : port number, default is 18080
    --folder  : provide file-download for web page, file stores, etc...
    --demo    : provide demo show and syntax highlight
Example:
    -p 18080
    -p 18080 --folder public --folder html
    -p 18080 --folder public --demo javascript
    '''


class Profile:
    fdr = dict()
    prt = 18080
    shows = dict()

    def __init__(self, port, folders, demos):
        if port.isdigit():
            self.prt = int(port) if 1024 < int(port) < 65536 else 18080
        for i in folders:
            if os.path.isdir(i):
                self.fdr[i] = 1
        for i in demos:
            if os.path.isdir(i):
                self.shows[i] = 1

    def debug(self):
        print "(port, folders, demos) = (%s, %s, %s)" % (
            self.port,
            ';'.join(self.folders),
            ';'.join(self.demos)
            )

    @property
    def port(self):
        return self.prt

    @property
    def folders(self):
        for i in sorted(self.fdr.keys()):
            yield i

    @property
    def demos(self):
        for i in sorted(self.shows.keys()):
            yield i


def parse_parameter(list_para):
    port = None
    file_folder = list()
    demo_folder = list()
    try:
        opts, args = getopt.getopt(list_para, 'hp:',
                                   ['help', 'folder=', 'demo='])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                return None
            elif opt == '-p':
                port = arg
            elif opt == '--folder':
                file_folder.append(arg)
            elif opt == '--demo':
                demo_folder.append(arg)
    except getopt.GetoptError as err:
        print str(err)
        return None
    return Profile(port=port, folders=file_folder, demos=demo_folder)


class ServiceRoot(Resource):
    isLeaf = False
    child_list = dict()  # name -> [0]link, [1]description

    def getChild(self, path, request):
        if path == '' or path == '/' or path == '/index.html':
            return self
        return Resource.getChild(self, path, request)

    def render_GET(self, request):
        buffer = list()
        buffer.append(prepare_html_start())
        buffer.append(prepare_table_start(['Link', 'Description']))
        for i in sorted(self.child_list.keys()):
            child = self.child_list[i]
            buffer.append(prepare_table_raw([
                "<a href=\"%s\">%s</a>" % (child[0], i), child[1]]
            ))
        buffer.append(prepare_table_stop())
        buffer.append(prepare_html_stop())
        return '\r\n'.join(buffer)

    def register_children(self, name, link, desc):
        if name not in self.child_list:
            self.child_list[name] = [link, desc]


class MyServer:

    def __init__(self, profile):
        self.root = ServiceRoot()
        self.factory = Site(self.root)
        self.profile = profile
        for i in self.profile.folders:
            name = i.lower()
            link = os.path.split(name)[-1]
            self.root.putChild(name, File(i))
            self.root.register_children(name, link, 'FILE for ' + name)

    def start(self):
        reactor.listenTCP(self.profile.port, self.factory)
        reactor.run()

    def plugin(self):
        self.root.putChild('returncode', Service_ReturnCode())
        self.root.register_children('Return Code', 'returncode',
                                    'emuninate all HTTP status code')
        self.root.putChild('calendar', Service_Calendar())
        self.root.register_children('Calendar', 'calendar',
                                    'Calendar for specific year')


if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        usage_help()
        sys.exit(0)
    profile = parse_parameter(sys.argv[1:])
    if profile is None:
        usage_help()
        sys.exit(0)
    server = MyServer(profile)
    server.plugin()
    server.start()
