import os
import sys
import mock
from mock import MagicMock

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import fake_filesystem_unittest

from aws_role_credentials.models import SamlAssertion, AwsCredentialsFile
from tests.helper import saml_assertion, read_config_file, Struct
from aws_role_credentials.actions import Actions

def load_tests(loader, tests, ignore):
    return fake_filesystem_unittest.load_doctests(loader, tests, ignore, example)

class TestActions(fake_filesystem_unittest.TestCase):
    TEST_FILE="/test/file"

    def setUp(self):
        self.setUpPyfakefs()
        os.mkdir('/test')

    def tearDown(self):
        pass

    @mock.patch('aws_role_credentials.actions.boto.sts')
    def test_credentials_are_generated_from_saml(self, mock_sts):
        mock_conn = MagicMock()
        mock_conn.assume_role_with_saml.return_value = Struct({'credentials':
                                                               Struct({'access_key': 'SAML_ACCESS_KEY',
                                                                       'secret_key': 'SAML_SECRET_KEY',
                                                                       'session_token': 'SAML_TOKEN'})})
        mock_sts.connect_to_region.return_value = mock_conn

        assertion = saml_assertion(['arn:aws:iam::1111:role/DevRole,arn:aws:iam::1111:saml-provider/IDP'])
        Actions(self.TEST_FILE,
                'test-profile', 'un-south-1').credentials_from_saml(assertion)

        assert read_config_file(self.TEST_FILE) == ['[test-profile]',
                                                    'output = json',
                                                    'region = un-south-1',
                                                    'aws_access_key_id = SAML_ACCESS_KEY',
                                                    'aws_secret_access_key = SAML_SECRET_KEY',
                                                    'aws_session_token = SAML_TOKEN',
                                                    '']

    @mock.patch('aws_role_credentials.actions.boto.sts')
    def test_credentials_are_generated_from_user(self, mock_sts):
        mock_conn = MagicMock()
        mock_conn.assume_role.return_value = Struct({'credentials':
                                                     Struct({'access_key': 'SAML_ACCESS_KEY',
                                                             'secret_key': 'SAML_SECRET_KEY',
                                                             'session_token': 'SAML_TOKEN'})})
        mock_sts.connect_to_region.return_value = mock_conn

        arn = 'arn:role/developer'
        session_name = 'dev-session'

        Actions(self.TEST_FILE,
                'test-profile', 'un-south-1').credentials_from_user(arn, session_name)

        mock_conn.assume_role.assert_called_with(arn, session_name,
                                                 mfa_serial_number=None,
                                                 mfa_token=None)


        assert read_config_file(self.TEST_FILE) == ['[test-profile]',
                                                    'output = json',
                                                    'region = un-south-1',
                                                    'aws_access_key_id = SAML_ACCESS_KEY',
                                                    'aws_secret_access_key = SAML_SECRET_KEY',
                                                    'aws_session_token = SAML_TOKEN',
                                                    '']

    @mock.patch('aws_role_credentials.actions.boto.sts')
    def test_mfa_is_passed_to_sts(self, mock_sts):
        mock_conn = MagicMock()
        mock_conn.assume_role.return_value = Struct({'credentials':
                                                     Struct({'access_key': 'SAML_ACCESS_KEY',
                                                             'secret_key': 'SAML_SECRET_KEY',
                                                             'session_token': 'SAML_TOKEN'})})
        mock_sts.connect_to_region.return_value = mock_conn

        arn = 'arn:role/developer'
        session_name = 'dev-session'

        Actions(self.TEST_FILE,
                'test-profile', 'un-south-1').credentials_from_user(arn, session_name,
                                                                    mfa_serial_number='arn:11111',
                                                                    mfa_token='123456')

        mock_conn.assume_role.assert_called_with(arn, session_name,
                                                 mfa_serial_number='arn:11111',
                                                 mfa_token='123456')
