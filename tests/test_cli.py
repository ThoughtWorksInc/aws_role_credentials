import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
from mock import Mock

from aws_role_credentials.cli import create_parser


class TestArgParsing(unittest.TestCase):
    def setUp(self):
        self.saml_action = Mock()
        self.user_action = Mock()
        self.parser = create_parser('test', None,
                                    self.saml_action,
                                    self.user_action)

    def test_profile_arg(self):
        parsed = self.parser.parse_args(['saml', '--profile', 'test'])
        self.assertEqual(parsed.profile, 'test')

    def test_profile_default(self):
        parsed = self.parser.parse_args(['saml'])
        self.assertEqual(parsed.profile, 'sts')

    def test_region_arg(self):
        parsed = self.parser.parse_args(['saml', '--region', 'un-test-1'])
        self.assertEqual(parsed.region, 'un-test-1')

    def test_region_default(self):
        parsed = self.parser.parse_args(['saml'])
        self.assertEqual(parsed.region, 'us-east-1')

    def test_exec_arg(self):
        parsed = self.parser.parse_args(['saml', '--exec', 'echo this'])
        self.assertEquals(parsed.exec_command, 'echo this')

    def test_saml_subcommand(self):
        parsed = self.parser.parse_args(['saml'])

        parsed.func()

        self.saml_action.assert_called_with()

    def test_user_subcommand(self):
        parsed = self.parser.parse_args(['user', 'test-arn', 'test-session'])

        self.assertEqual(parsed.role_arn, 'test-arn')
        self.assertEqual(parsed.session_name, 'test-session')

        parsed.func()

        self.user_action.assert_called_with()

    def test_user_subcommand_requires_positional_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['user'])

    def test_user_subcommand_requires_session_name(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['user', 'role-arn'])

    def test_user_subcommand_with_mfa(self):
        parsed = self.parser.parse_args(['user', 'test-arn', 'test-session',
                                         '--mfa-serial-number', 'test-mfa-serial',
                                         '--mfa-token', 'test-mfa-token'])

        self.assertEqual(parsed.role_arn, 'test-arn')
        self.assertEqual(parsed.session_name, 'test-session')
        self.assertEqual(parsed.mfa_serial_number, 'test-mfa-serial')
        self.assertEqual(parsed.mfa_token, 'test-mfa-token')

        parsed.func()

        self.user_action.assert_called_with()
