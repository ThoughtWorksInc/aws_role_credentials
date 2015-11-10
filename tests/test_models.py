#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aws_role_credentials
----------------------------------

Tests for `aws_role_credentials` module.
"""

import unittest

from aws_role_credentials.models import SamlAssertion


class TestModels(unittest.TestCase):
    def saml_assertion(self, roles):
        attribute_value = '''<saml2:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">
                   {0}
                 </saml2:AttributeValue>'''

        roles_values = [(attribute_value.format(x)) for x in roles]

        return '''<?xml version="1.0" encoding="UTF-8"?>
        <saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" Version="2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema">
           <saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" ID="id17773561036281221470153530" IssueInstant="2015-11-06T10:48:25.399Z" Version="2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema">
             <saml2:AttributeStatement xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">
               <saml2:Attribute Name="https://aws.amazon.com/SAML/Attributes/Role" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
                  {0}
               </saml2:Attribute>
             </saml2:AttributeStatement>
           </saml2:Assertion>
        </saml2p:Response>'''.format("".join(roles_values))

    def test_roles_are_extracted(self):
        assertion = self.saml_assertion(['arn:aws:iam::1111:role/DevRole,arn:aws:iam::1111:saml-provider/IDP'])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'}]

    def test_principle_can_be_first(self):
        assertion = self.saml_assertion(['arn:aws:iam::1111:saml-provider/IDP, arn:aws:iam::1111:role/DevRole'])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'}]

    def test_white_space_is_removed(self):
        assertion = self.saml_assertion([' arn:aws:iam::1111:saml-provider/IDP ,  arn:aws:iam::1111:role/DevRole '])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'}]

    def test_multiple_roles_are_returned(self):
        assertion = self.saml_assertion(['arn:aws:iam::1111:role/DevRole,arn:aws:iam::1111:saml-provider/IDP',
                                         'arn:aws:iam::2222:role/QARole,arn:aws:iam::2222:saml-provider/IDP'])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'},
                                                    {'role': 'arn:aws:iam::2222:role/QARole',
                                                     'principle': 'arn:aws:iam::2222:saml-provider/IDP'}]


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
