import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
from mock import Mock

from aws_role_credentials.cli import create_parser

class TestArgParsing(unittest.TestCase):
    def setUp(self):
        self.mock_actions = {'saml': Mock(),
                             'user': Mock()}
        self.parser = create_parser('test', None, self.mock_actions)

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

    def test_saml_subcommand(self):
        parsed = self.parser.parse_args(['saml'])

        parsed.func()

        self.mock_actions['saml'].assert_called_with()

    def test_user_subcommand(self):
        parsed = self.parser.parse_args(['user', 'test-arn', 'test-session'])

        self.assertEqual(parsed.role_arn, 'test-arn')
        self.assertEqual(parsed.session_name, 'test-session')

        parsed.func()

        self.mock_actions['user'].assert_called_with()

    def test_user_subcommand_requires_positional_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['user'])

    def test_user_subcommand_requires_session_name(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['user', 'role-arn'])
