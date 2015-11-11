# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import ConfigParser
import base64

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
        return base64.b64encode(self.assertion)

class AwsCredentialsFile:
    def __init__(self, filename):
        self.filename = filename
        return

    def _add_profile(self, name, profile):
        config = ConfigParser.RawConfigParser()
        config.read(self.filename)

        if not config.has_section(name):
            config.add_section(name)

        [(config.set(name, k, v))
         for k,v in profile.iteritems()]

        with open(self.filename, 'w+') as configfile:
            config.write(configfile)

    def add_profile(self, name, region, credentials):
        self._add_profile(name, {'output': 'json',
                                 'region': region,
                                 'aws_access_key_id': credentials.access_key,
                                 'aws_secret_access_key': credentials.secret_key,
                                 'aws_session_token': credentials.session_token})
