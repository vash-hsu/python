#!/usr/bin/env python


def prepare_html_start():
    return '<!DOCTYPE html><html><body>'


def prepare_html_stop():
    return '</html></body>'


def prepare_table_start(fields):
    return "<table border='3'><tr>" +\
           '\r\n'.join(["<th>%s</th>" % i for i in fields])+\
           "</tr>"


def prepare_table_raw(fields):
    return "<tr>" + '\r\n'.join(["<td>%s</td>" % i for i in fields]) + "</tr>"


def prepare_table_stop():
    return "</table>"


def prepare_script_section(lines):
    return '<script>\r\n' + ''.join(lines) + '</script>\r\n'


def prepare_script_highlight_section(lines):
    cooked = []
    for i in lines:
        temp = i.replace('&', '&amp;')
        temp = temp.replace('<', '&lt;')
        temp = temp.replace('>', '&gt;')
        cooked.append(temp)

    return '<script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js"></script>\r\n' +\
           '<pre class="prettyprint linenums:1">\r\n' +\
           ''.join(cooked) + \
           '</pre>\r\n'
