import os
import sys
import mock
from mock import MagicMock

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from pyfakefs import fake_filesystem_unittest
import six

from tests.helper import saml_assertion, read_config_file, Struct
from aws_role_credentials.actions import Actions


class TestActions(unittest.TestCase):
    @mock.patch('aws_role_credentials.actions.boto.sts')
    def test_credentials_are_generated_from_saml(self, mock_sts):
        stub_token = Struct({'credentials': None})
        mock_conn = MagicMock()
        mock_conn.assume_role_with_saml.return_value = stub_token
        mock_sts.connect_to_region.return_value = mock_conn

        assertion = saml_assertion(['arn:aws:iam::1111:role/DevRole,arn:aws:iam::1111:saml-provider/IDP'])

        token = Actions.saml_token('un-south-1', assertion)

        self.assertEqual(token, stub_token)

    @mock.patch('aws_role_credentials.actions.boto.sts')
    def test_credentials_are_generated_from_user(self, mock_sts):
        stub_token = Struct({'credentials': None})

        mock_conn = MagicMock()
        mock_conn.assume_role.return_value = stub_token
        mock_sts.connect_to_region.return_value = mock_conn

        arn = 'arn:role/developer'
        session_name = 'dev-session'

        token = Actions.user_token('un-south-1',
                                   arn, session_name)

        mock_conn.assume_role.assert_called_with(arn, session_name,
                                                 mfa_serial_number=None,
                                                 mfa_token=None)

        self.assertEqual(token, stub_token)

    @mock.patch('aws_role_credentials.actions.boto.sts')
    def test_mfa_is_passed_to_sts(self, mock_sts):
        stub_token = Struct({'credentials': None})

        mock_conn = MagicMock()
        mock_conn.assume_role.return_value = stub_token
        mock_sts.connect_to_region.return_value = mock_conn

        arn = 'arn:role/developer'
        session_name = 'dev-session'

        Actions.user_token('un-south-1',
                           arn, session_name,
                           mfa_serial_number='arn:11111',
                           mfa_token='123456')

        mock_conn.assume_role.assert_called_with(arn, session_name,
                                                 mfa_serial_number='arn:11111',
                                                 mfa_token='123456')

    @mock.patch('aws_role_credentials.actions.Popen')
    def test_exec_setups_environment_variables(self, mock_popen):
        token = Struct({'credentials':
                        Struct({'access_key': 'TEST_ACCESS_KEY',
                                'secret_key': 'TEST_SECRET_KEY',
                                'session_token': 'TEST_TOKEN',
                                'expiration': 'TEST_EXPIRATION'})})

        with mock.patch('os.environ') as mock_env:
            mock_env.copy.return_value = {}

            Actions.exec_with_credentials('un-south-1',
                                          'echo hello', token)

            mock_popen.assert_called_with(['echo', 'hello'],
                                          env={'AWS_ACCESS_KEY_ID': 'TEST_ACCESS_KEY',
                                               'AWS_DEFAULT_REGION': 'un-south-1',
                                               'AWS_SECRET_ACCESS_KEY': 'TEST_SECRET_KEY',
                                               'AWS_SESSION_TOKEN': 'TEST_TOKEN'},
                                          shell=False)


class TestConfigActions(fake_filesystem_unittest.TestCase):
    TEST_FILE = "/test/file"

    def setUp(self):
        self.setUpPyfakefs()
        os.mkdir('/test')

    def tearDown(self):
        pass

    def test_credentials_are_generated_from_token(self):
        token = Struct({'credentials':
                        Struct({'access_key': 'SAML_ACCESS_KEY',
                                'secret_key': 'SAML_SECRET_KEY',
                                'session_token': 'SAML_TOKEN',
                                'expiration': 'TEST_EXPIRATION'})})

        Actions.persist_credentials(self.TEST_FILE,
                                    'test-profile',
                                    'un-south-1', token, True)

        six.assertCountEqual(self, read_config_file(self.TEST_FILE),
                             ['[test-profile]',
                              'output = json',
                              'region = un-south-1',
                              'aws_access_key_id = SAML_ACCESS_KEY',
                              'aws_secret_access_key = SAML_SECRET_KEY',
                              'aws_security_token = SAML_TOKEN',
                              'aws_session_token = SAML_TOKEN',
                              ''])
