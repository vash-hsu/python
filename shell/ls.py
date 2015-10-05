#!/usr/bin/env python

# from
# http://www.pixelbeat.org/talks/python/ls.py.html

import sys
import stat
import os
import getpass
import locale
import time


def get_permission_notation(target):
    permission = '-'
    link = ''
    # dir, file or link
    if os.path.isdir(target):
        permission = 'd'
    elif os.path.islink(target):
        permission = 'l'
        link = os.path.realpath(target)
    # mode
    mode = stat.S_IMODE(os.lstat(target).st_mode)
    for who in "USR", "GRP", "OTH":
        for what in "R", "W", "X":
            if mode & getattr(stat,"S_I"+what+who):
                permission += what.lower()
            else:
                permission += "-"
    return permission, link


def get_nlink(target):
    return "%d" % os.lstat(target).st_nlink


def get_uid(target):
    uid = os.lstat(target).st_uid
    try:
        #return "%s" % pwd.getpwuid(uid)[0]
        return "%s" % getpass.getuser()
    except KeyError:
        return uid


def get_gid(target):
    try:
        import grp
        try:
            gid = os.lstat(target).st_gid
            return "%s" % grp.getgrgid(gid)[0]
        except KeyError:
            return gid
    except ImportError:
        return '-'


def get_size(target):
    return "%d" % os.lstat(target).st_size


def get_time(target):
    timestamp = os.lstat(target).st_mtime
    time_fmt = "%Y-%m-%d %H:%M:%S"
    return time.strftime(time_fmt, time.gmtime(timestamp))
    # now = int(time.time())
    # # 6 months ago or not
    # six_months_ago = now - (6*30*24*60*60)
    # time_fmt = "%Y/%m/%d "
    # if (timestamp < six_months_ago) or (timestamp > now): # or in the future
    #     #time_fmt = "%b %e  %Y"
    #     time_fmt = "%m/%d %Y"
    # else:
    #     #time_fmt = "%b %e %R"
    #     time_fmt = "%m/%d %H:%M:%S"
    # return time.strftime(time_fmt, time.gmtime(timestamp))


def ls(filename, root):
    # validate if it is real existent
    target = os.path.join(root, filename)
    if not os.path.exists(target):
        return ''
    #
    perms, link = get_permission_notation(target)
    nlink = get_nlink(target)
    name = get_uid(target)
    group = get_gid(target)
    size = get_size(target)
    time = get_time(target)
    if link:
        link = ' -> ' + link
    return perms, nlink, name, group, size, time, filename, link


def ls_print_singleline(part):
    print ' '.join(part)


def ls_print_multiline(parts):
    #perms, nlink, name, group, size, time, filename, link
    space4link = 1
    space4name = 1
    space4group = 1
    space4size = 1
    space4date = 1
    for i in parts:
        space4link = max(len(i[1]), space4link)
        space4name = max(len(i[2]), space4name)
        space4group = max(len(i[3]), space4group)
        space4size = max(len(i[4]), space4size)
        space4date = max(len(i[5]), space4date)
    form_str = "%s " + "%%%ds %%%ds %%%ds %%%ds %%%ds" \
               % (space4link, space4name, space4group, space4size, space4date) \
               + " %s %s"
    #print form_str
    for i in parts:
        print form_str % i


def ls_dir(input_path):
    children = os.listdir(input_path)
    # Do locale sensitive sort of files to list
    locale.setlocale(locale.LC_ALL, '')
    children.sort(locale.strcoll)
    buffer_out = []
    for child in children:
        if child == '.':
            continue
        # perms, nlink, name, group, size, time, filename, link
        buffer_out.append(ls(child, input_path))
    #
    if len(buffer_out) == 0:
        return False
    elif len(buffer_out) == 1:
        ls_print_singleline(buffer_out[0])
    if len(buffer_out) > 1:
        ls_print_multiline(buffer_out)
    return True


def ls_prepare(i):
    if i == '.':
        ls_dir('.')
    elif os.path.isdir(i):
        ls_dir(i)
    elif os.path.isfile(i):
        ls_print_singleline(ls(i, '.'))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        ls_prepare('.')
    else:
        for i in sys.argv[1:]:
            ls_prepare(i)
