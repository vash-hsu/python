#!/usr/bin/env python


from SmtpUtil import uuid, timestamp
from SmtpServer import host_smtpd, Profile, whoami, debugger, logger
import os
import sys
from functools import partial
import email
import mimetypes

'''
# porting from Perl to Python
Purpose
   Outlook --> SMTP 127.0.0.1 --> 25 port listened by SMTP2EML
   --> create folder under working directory
   --> save raw mail from SMTP protocol in name/form of
       Sub-Folder: SHA1(email address)
       each Email:
           YearMonthDay-HourMinuteSecond-SHA1.eml
   --> save attachment into
       YearMonthDay-HourMinuteSecond/MyFilename.MyExt
   --> save attached RFC822 into
       YearMonthDay-HourMinuteSecond/SHA1.eml
  (to do)
   --> to support cross-platform under unit test cases
'''


Version = '20160109-v0.6'


def unicode_convert(buffer_src, charset_src, charset_dst):
    try:
        textdata = unicode(buffer_src, charset_src)
        textdata = textdata.encode(charset_dst, 'ignore')
    except UnicodeDecodeError:
        debugger("ERROR: UnicodeDecodeError, covert from %s " % charset_src)
        return ''
    except UnicodeEncodeError:
        debugger("ERROR: UnicodeDecodeError, covert to %s " % charset_dst)
        return ''
    return textdata


def unicode_convert_safely(buffer_src, charset_src, charset_dst):
    try:
        return unicode_convert(buffer_src, charset_src, charset_dst)
    except BaseException as err:
        debugger("ERROR: Exception: %s" % str(err))
        return ''


class EMLReader:

    def __init__(self, raw_string):
        self._email = None
        self._attachs = dict()
        if raw_string and len(raw_string) > 0:
            try:
                self._email = email.message_from_string(raw_string)
            except BaseException as err:
                debugger("Exception: %s" % str(err))
                self._email = None
            if self._email:
                self._retrieve_attachment()

    @staticmethod
    def _normalize_rfc822_entity(message):
        if not message:
            return ''
        else:
            try:
                # debugger(repr(message))
                terms = message.split('\n\n')  # how about platform dependent?
                return '\n\n'.join(terms[1:])
            except BaseException as err:
                print "ERROR: %s" % str(err)
                return ''

    # package[payload_uuid] = (filename_candidate, payload)
    def _parse_eml_to_name_payload(self, email_msg, package):
        main_type = email_msg.get_content_maintype()
        cont_type = email_msg.get_content_type()
        # debugger("%s %s" % (main_type, cont_type))
        if 'multipart' in main_type.lower():
            return False
        elif 'message/rfc822' == cont_type:
            payload = self._normalize_rfc822_entity(email_msg.as_string())
            # debugger("payload = %s" % repr(payload))
            if payload:
                payload_uuid = uuid(payload)
                package[payload_uuid] = (payload_uuid + '.eml', payload)
                return True
        # i.e. text/html, text/plain which has no filename field
        elif 'text' in main_type.lower() and \
                '~oops~' == email_msg.get_filename('~oops~'):
            return False
        else:  # attachment
            payload = email_msg.get_payload(None, True)
            if not payload or len(payload) == 0:
                return False
            payload_uuid = uuid(payload)
            # filename matter?
            field_filename = email_msg.get_filename('')  # if fail, return ''
            if len(field_filename) > 0:
                if '=?' in field_filename and '?=' in field_filename:
                    name = email.Utils.\
                        collapse_rfc2231_value(field_filename).strip()
                    (filename, charset) = email.Header.decode_header(name)[0]
                    if charset and len(charset) > 0:
                        field_filename = unicode_convert_safely(filename,
                                                                charset,
                                                                'utf-8')
                field_filename = os.path.split(field_filename)[1]
            else:
                field_filename = payload_uuid
            name, ext = os.path.splitext(field_filename)
            if len(ext) == 0:
                ext = mimetypes.guess_extension(cont_type)
            if not ext or len(ext) < 2: # .exe, .js, .x
                ext = '.bin'
            filename_candidate = name + ext
            package[payload_uuid] = (filename_candidate, payload)
            return True
        return False

    def _retrieve_attachment(self):
        if not self._email:
            return False
        if not self._email.is_multipart():
            package = dict()
            if self._parse_eml_to_name_payload(self._email, package):
                self._attachs.update(package)
        else:
            for each_part in self._email.walk():
                package = dict()
                if self._parse_eml_to_name_payload(each_part, package):
                    self._attachs.update(package)
        return True

    @property
    def attachments(self):
        for str_uuid in self._attachs.keys():
            yield [str_uuid, ] + list(self._attachs[str_uuid])
        pass


class Profile4LocalStore(Profile):
    
    def __init__(self):
        # super().__init__()
        Profile.__init__(self)
        self.config['folder'] = '.mailstore'

    @property
    def folder(self):
        return self.config[whoami()]


def write_file_to_disk(folder, filename, payload):
    if not os.path.exists(folder):
        os.makedirs(folder)
    if os.path.isdir(folder):
        target_path = os.path.join(folder, filename)
        with open(target_path, 'wb') as writer:
            writer.write(payload)
    else:
        debugger("ERROR: %s is not valid target folder" % folder)


def write_file_to_disk_safely(folder, filename, payload):
    try:
        write_file_to_disk(folder, filename, payload)
    except BaseException as err:
        debugger("ERROR: Exception " + str(err))
        return False
    return True


def write_mail_content_to_eml(folder_path, to_address, message):
    ts = timestamp()
    message_id = "%s-%s" % (ts, uuid(message))
    # phase 1
    for i in to_address:
        # security issue if address give us surprise
        base_path = os.path.join(folder_path, uuid(i.lower()))
        write_file_to_disk_safely(base_path, message_id + '.eml', message)
    # phase 2
    if message:
        email_reader = EMLReader(message)
        for str_uuid, filename, payload in email_reader.attachments:
            # debugger("process %s" % filename)
            write_file_to_disk_safely(os.path.join(folder_path, ts),
                                      filename, payload)


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
