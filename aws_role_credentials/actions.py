# -*- coding: utf-8 -*-

import boto.sts

from aws_role_credentials.models import SamlAssertion, AwsCredentialsFile

class Actions:

    def __init__(self, credentials_filename,
                 profile,
                 region):
                 self.credentials_filename = credentials_filename
                 self.profile = profile
                 self.region = region

    @staticmethod
    def persist_credentials(credentials_filename,
                            profile, region, token):
        AwsCredentialsFile(credentials_filename).add_profile(profile,
                                                             region,
                                                             token.credentials)
    def credentials_handler(self):
        return lambda token: Actions.persist_credentials(self.credentials_filename,
                                                    self.profile,
                                                    self.region,
                                                    token)

    @staticmethod
    def saml_token(region, assertion):
        assertion = SamlAssertion(assertion)
        role = assertion.roles()[0]

        conn = boto.sts.connect_to_region(region, anon=True)
        return conn.assume_role_with_saml(role['role'], role['principle'],
                                          assertion.encode())

    @staticmethod
    def user_token(region, arn, session_name,
                   mfa_serial_number=None, mfa_token=None):
        conn = boto.sts.connect_to_region(region)

        return conn.assume_role(arn, session_name,
                                mfa_serial_number=mfa_serial_number,
                                mfa_token=mfa_token)

    def credentials_from_saml(self, assertion):
        token = self.saml_token(self.region, assertion)

        self.credentials_handler()(token)

    def credentials_from_user(self, arn, session_name,
                              mfa_serial_number=None, mfa_token=None):

        token = self.user_token(self.region,
                                arn, session_name,
                                mfa_serial_number, mfa_token)

        self.credentials_handler()(token)
