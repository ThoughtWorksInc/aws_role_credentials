#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aws_role_credentials
----------------------------------

Tests for `aws_role_credentials` module.
"""
import os
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from pyfakefs import fake_filesystem_unittest
import six

from tests.helper import saml_assertion, write_config_file, read_config_file, Struct
from aws_role_credentials.models import SamlAssertion, AwsCredentialsFile


class TestSamlAssertion(unittest.TestCase):
    def test_roles_are_extracted(self):
        assertion = saml_assertion(['arn:aws:iam::1111:role/DevRole,arn:aws:iam::1111:saml-provider/IDP'])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'}]

    def test_principle_can_be_first(self):
        assertion = saml_assertion(['arn:aws:iam::1111:saml-provider/IDP, arn:aws:iam::1111:role/DevRole'])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'}]

    def test_white_space_is_removed(self):
        assertion = saml_assertion([' arn:aws:iam::1111:saml-provider/IDP ,  arn:aws:iam::1111:role/DevRole '])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'}]

    def test_multiple_roles_are_returned(self):
        assertion = saml_assertion(['arn:aws:iam::1111:role/DevRole,arn:aws:iam::1111:saml-provider/IDP',
                                    'arn:aws:iam::2222:role/QARole,arn:aws:iam::2222:saml-provider/IDP'])

        assert SamlAssertion(assertion).roles() == [{'role': 'arn:aws:iam::1111:role/DevRole',
                                                     'principle': 'arn:aws:iam::1111:saml-provider/IDP'},
                                                    {'role': 'arn:aws:iam::2222:role/QARole',
                                                     'principle': 'arn:aws:iam::2222:saml-provider/IDP'}]

    def test_assertion_is_encoded(self):
        assert SamlAssertion("test encoding").encode() == b'dGVzdCBlbmNvZGluZw=='


class TestAwsCredentialsFile(fake_filesystem_unittest.TestCase):
    TEST_FILE = "/test/file"

    def setUp(self):
        self.setUpPyfakefs()
        os.mkdir('/test')

    def tearDown(self):
        pass

    def test_profile_is_added(self):
        AwsCredentialsFile(self.TEST_FILE).add_profile(
            'dev', 'un-west-5', Struct({'access_key': 'ACCESS_KEY',
                                        'secret_key': 'SECRET_KEY',
                                        'session_token': 'SESSION_TOKEN',
                                        'expiration': 'TEST_EXPIRATION'}))

        six.assertCountEqual(self, read_config_file(self.TEST_FILE),
                             ['[dev]',
                              'output = json',
                              'region = un-west-5',
                              'aws_access_key_id = ACCESS_KEY',
                              'aws_secret_access_key = SECRET_KEY',
                              'aws_security_token = SESSION_TOKEN',
                              'aws_session_token = SESSION_TOKEN',
                              ''])

    def test_profile_is_updated(self):
        write_config_file(self.TEST_FILE,
                          '[dev]',
                          'output = none',
                          'region = us-west-2',
                          'aws_access_key_id = OLD',
                          'aws_secret_access_key = REDUNDANT',
                          'aws_session_token = EXPIRED')

        AwsCredentialsFile(self.TEST_FILE).add_profile(
            'dev', 'un-west-5', Struct({'access_key': 'ACCESS_KEY',
                                        'secret_key': 'SECRET_KEY',
                                        'session_token': 'SESSION_TOKEN',
                                        'expiration': 'TEST_EXPIRATION'}))

        six.assertCountEqual(self, read_config_file(self.TEST_FILE),
                             ['[dev]',
                              'region = un-west-5',
                              'aws_access_key_id = ACCESS_KEY',
                              'aws_secret_access_key = SECRET_KEY',
                              'output = json',
                              'aws_security_token = SESSION_TOKEN',
                              'aws_session_token = SESSION_TOKEN',
                              ''])

    def test_existing_profiles_are_preserved(self):
        write_config_file(self.TEST_FILE,
                          '[test]',
                          'output = none',
                          'region = us-west-2',
                          'aws_access_key_id = TEST_KEY',
                          'aws_secret_access_key = TEST_ACCESS',
                          'aws_security_token = TEST_TOKEN',
                          'aws_session_token = TEST_TOKEN')

        AwsCredentialsFile(self.TEST_FILE).add_profile(
            'dev', 'un-west-5', Struct({'access_key': 'ACCESS_KEY',
                                        'secret_key': 'SECRET_KEY',
                                        'security_token': 'SESSION_TOKEN',
                                        'session_token': 'SESSION_TOKEN',
                                        'expiration': 'TEST_EXPIRATION'}))

        six.assertCountEqual(self, read_config_file(self.TEST_FILE),
                             ['[test]',
                              'region = us-west-2',
                              'aws_access_key_id = TEST_KEY',
                              'aws_secret_access_key = TEST_ACCESS',
                              'output = none',
                              'aws_security_token = TEST_TOKEN',
                              'aws_session_token = TEST_TOKEN',
                              '',
                              '[dev]',
                              'output = json',
                              'region = un-west-5',
                              'aws_access_key_id = ACCESS_KEY',
                              'aws_secret_access_key = SECRET_KEY',
                              'aws_security_token = SESSION_TOKEN',
                              'aws_session_token = SESSION_TOKEN',
                              ''])


if __name__ == '__main__':
    sys.exit(unittest.main())
