import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from aws_role_credentials.cli import create_parser

class TestArgParsing(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser('test', None)

    def test_profile_arg(self):
        parsed = self.parser.parse_args(['--profile', 'test'])
        self.assertEqual(parsed.profile, 'test')

    def test_profile_defaults_to_sts(self):
        parsed = self.parser.parse_args([])
        self.assertEqual(parsed.profile, 'sts')
