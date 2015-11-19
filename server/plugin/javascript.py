#!/usr/bin/env python

# twisted
from twisted.web.resource import Resource
from htmlwritter import *
from services import convert_path_to_name_path_pair
import os


class JavaScriptInterpreter(Resource):

    def __init__(self, name, folder):
        Resource.__init__(self)
        self.scriptname = name
        self.folder = folder

    def render_GET(self, request):
        content = list()
        content.append(prepare_html_start())

        content.append("%s" % self.scriptname)
        file_path = os.path.join(self.folder, self.scriptname)
        if os.path.exists(file_path):
            with open(file_path, 'r') as fread:
                page = fread.readlines()
                content.append(prepare_script_section(page))
                content.append(prepare_script_highlight_section(page))
        content.append(prepare_html_stop())
        return '\r\n'.join(content)


class Service_JavaScript(Resource):

    def __init__(self, base):
        Resource.__init__(self)
        self.folder = base

    def getChild(self, name, request):
        if name == '' or name == '/' or name == '/index.html':
            return self
        else:
            return JavaScriptInterpreter(name, self.folder)

    def render_GET(self, request):
        candidate = dict()
        content = list()
        uri = request.uri
        for root, dirs, files in os.walk(self.folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                name, ext = os.path.splitext(filename)
                if ext not in ['.js', '.py']:
                    continue
                if os.path.isfile(filepath):
                    name, path = convert_path_to_name_path_pair(filepath)
                    candidate[name] = path
        content.append(prepare_html_start())
        content.append(prepare_table_start(['Link', 'Location']))
        for i in sorted(candidate.keys()):
            content.append(prepare_table_raw([
                "<a href=\"%s/%s\">%s</a>" % (uri, i, i),
                candidate[i]]))
        content.append(prepare_table_stop())
        content.append(prepare_html_stop())
        return '\r\n'.join(content)

