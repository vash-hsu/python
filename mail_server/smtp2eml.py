#!/usr/bin/env python


from SmtpUtil import uuid, timestamp
from SmtpServer import host_smtpd, Profile, whoami, debugger, logger
import os
import sys
from functools import partial

'''
# porting from Perl to Python
Purpose
   Outlook --> SMTP 127.0.0.1 --> 25 port listened by SMTP2EML
   --> create folder under working directory
   --> save raw mail from SMTP protocol in name/form of
       Sub-Folder: SHA1(email address)
       each Email:
           YearMonthDay-HourMinuteSecond-SHA1.eml
  (to do)
   --> save attached RFC822
       into YearMonthDay-HourMinuteSecond\00000001.eml
       into YearMonthDay-HourMinuteSecond\00000002.eml
'''


Version = '20160107-v0.5'


class Profile4LocalStore(Profile):
    
    def __init__(self):
        # super().__init__()
        Profile.__init__(self)
        self.config['folder'] = '.mailstore'

    @property
    def folder(self):
        return self.config[whoami()]


def write_mail_content_to_eml(folder_path, to_address, message):
    message_id = "%s-%s" % (timestamp(), uuid(message))
    for i in to_address:
        # security issue if address give us surprise
        base_path = os.path.join(folder_path, uuid(i.lower()))
        try:
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            if os.path.isdir(base_path):
                eml_path = os.path.join(base_path, message_id + '.eml')
                with open(eml_path, 'wb') as writer:
                    writer.write(message)
        except BaseException as err:
            debugger("Exception: %s" % str(err))


if __name__ == "__main__":
    # configuration
    configuration = Profile4LocalStore()
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
    configuration.setup('logger', logger)
    # configuration.setup('debug', debugger)
    mail_data_writer = partial(write_mail_content_to_eml,
                               folder_path=configuration.folder)
    host_smtpd(configuration, cb_mailbody=mail_data_writer)
