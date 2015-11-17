# -*- coding: utf-8 -*-

import boto.sts

from aws_role_credentials.models import SamlAssertion, AwsCredentialsFile

class Actions:

    def __init__(self, credentials_filename,
                 profile,
                 region):
                 self.credentials_file = AwsCredentialsFile(credentials_filename)
                 self.profile = profile
                 self.region = region

    def credentials_from_saml(self, assertion):
        assertion = SamlAssertion(assertion)
        role = assertion.roles()[0]

        conn = boto.sts.connect_to_region(self.region, anon=True)
        token = conn.assume_role_with_saml(role['role'], role['principle'],
                                           assertion.encode())

        self.credentials_file.add_profile(self.profile,
                                          self.region,
                                          token.credentials)

    def credentials_from_user(self, arn, session_name,
                              mfa_serial_number=None, mfa_token=None):
        conn = boto.sts.connect_to_region(self.region)

        token = conn.assume_role(arn, session_name,
                                 mfa_serial_number=mfa_serial_number,
                                 mfa_token=mfa_token)

        self.credentials_file.add_profile(self.profile,
                                          self.region,
                                          token.credentials)
