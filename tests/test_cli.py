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

    def test_profile_default(self):
        parsed = self.parser.parse_args([])
        self.assertEqual(parsed.profile, 'sts')

    def test_region_arg(self):
        parsed = self.parser.parse_args(['--region', 'un-test-1'])
        self.assertEqual(parsed.region, 'un-test-1')

    def test_region_default(self):
        parsed = self.parser.parse_args([])
        self.assertEqual(parsed.region, 'us-east-1')
