# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

class SamlAssertion:

    def __init__(self, assertion):
        self.assertion = ET.fromstring(assertion)

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
        attributes = self.assertion.getiterator('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute')

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
