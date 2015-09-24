#!/usr/bin/env python

# from
# http://www.pixelbeat.org/talks/python/ls.py.html

import sys
import stat
import os
import grp
import pwd
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
        return "%s" % pwd.getpwuid(uid)[0]
    except KeyError:
        return uid


def get_gid(target):
    gid = os.lstat(target).st_gid
    try:
        return "%s" % grp.getgrgid(gid)[0]
    except KeyError:
        return gid


def get_size(target):
    return "%d" % os.lstat(target).st_size


def get_time(target):
    timestamp = os.lstat(target).st_mtime
    now = int(time.time())
    # 6 months ago or not
    six_months_ago = now - (6*30*24*60*60)
    if (timestamp < six_months_ago) or (timestamp > now): # ? not quite sure why > now
        time_fmt = "%b %e  %Y"
    else:
        time_fmt = "%b %e %R"
    return time.strftime(time_fmt, time.gmtime(timestamp))


def ls(filename, root):
    # validate if it is real existent
    target = os.path.join(root, filename)
    if not os.path.exists(target):
        return False
    #
    perms, link = get_permission_notation(target)
    nlink = get_nlink(target)
    name = get_uid(target)
    group = get_gid(target)
    size = get_size(target)
    time = get_time(target)
    #
    sys.stdout.write("%s %s %s %s %s %s " % (perms, nlink, name, group, size, time))
    sys.stdout.write(filename)
    if link:
        sys.stdout.write(" -> ")
    print link


def ls_dir(input_path):
    children = os.listdir(input_path)
    # Do locale sensitive sort of files to list
    locale.setlocale(locale.LC_ALL, '')
    children.sort(locale.strcoll)
    for child in children:
        if child == '.':
            continue
        ls(child, input_path)
    return True


def ls_prepare(i):
    if i == '.':
        ls_dir('.')
    elif os.path.isdir(i):
        ls_dir(i)
    elif os.path.isfile(i):
        ls(i)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        ls_prepare('.')
    else:
        for i in sys.argv[1:]:
            ls_prepare(i)
