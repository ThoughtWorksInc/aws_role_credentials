# -*- coding: utf-8 -*-

import sys
import base64
import configparser
import xml.etree.ElementTree as ET

# Support Python 2 and 3
py_version = sys.version_info.major
if py_version == 2:
    def toUnicode( string ):
        return unicode(string)
else:
    def toUnicode( string ):
        return string

class SamlAssertion:

    def __init__(self, assertion):
        self.assertion = assertion

    @staticmethod
    def split_roles(roles):
        return [(y.strip())
                for y
                in roles.text.split(',')]

    @staticmethod
    def sort_roles(roles):
        return sorted(roles,
                      key=lambda role: 'saml-provider' in role)

    def roles(self):
        attributes = ET.fromstring(self.assertion).getiterator('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute')

        roles_attributes = [x for x
                            in attributes
                            if x.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role']

        roles_values = [(x.getiterator('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'))
                        for x
                        in roles_attributes]

        return [(dict(zip(['role', 'principle'],
                          self.sort_roles(self.split_roles(x)))))
                for x
                in roles_values[0]]

    def encode(self):
        return base64.b64encode(self.assertion.encode('utf8'))


class AwsCredentialsFile:

    def __init__(self, filename):
        self.filename = filename
        return

    def _add_profile(self, name, profile):

        config = configparser.ConfigParser(interpolation=None)
        try:
            config.read_file(open(self.filename, 'r'))
        except:
            pass

        if not config.has_section(name):
            config.add_section(name)

        [(config.set(name, k, v))
         for k, v in profile.items()]

        with open(self.filename, 'w+') as configfile:
            config.write(configfile)

    def add_profile(self, name, region, credentials):
        name = toUnicode(name)
        self._add_profile(name, {u'output': u'json',
                                 u'region': toUnicode(region),
                                 u'aws_access_key_id': toUnicode(credentials.access_key),
                                 u'aws_secret_access_key': toUnicode(credentials.secret_key),
                                 u'aws_security_token': toUnicode(credentials.session_token),
                                 u'aws_session_token': toUnicode(credentials.session_token)})
