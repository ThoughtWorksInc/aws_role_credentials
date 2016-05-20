# -*- coding: utf-8 -*-

import base64
import configparser
import xml.etree.ElementTree as ET


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
        name = unicode(name)
        self._add_profile(name, {u'output': u'json',
                                 u'region': unicode(region),
                                 u'aws_access_key_id': unicode(credentials.access_key),
                                 u'aws_secret_access_key': unicode(credentials.secret_key),
                                 u'aws_security_token': unicode(credentials.session_token),
                                 u'aws_session_token': unicode(credentials.session_token)})
