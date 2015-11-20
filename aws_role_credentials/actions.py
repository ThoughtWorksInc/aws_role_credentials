# -*- coding: utf-8 -*-

import os
import boto.sts
import shlex
from subprocess import Popen

from aws_role_credentials.models import SamlAssertion, AwsCredentialsFile

class Actions:

    def __init__(self,
                 credentials_filename,
                 profile,
                 region,
                 **kwargs):

        self.credentials_filename = credentials_filename
        self.profile = profile
        self.region = region

    @staticmethod
    def persist_credentials(credentials_filename,
                            profile, region, token):
        AwsCredentialsFile(credentials_filename).add_profile(profile,
                                                             region,
                                                             token.credentials)
    @staticmethod
    def credentials_handler(credentials_filename,
                            profile,
                            region, **kwargs):
        return lambda token: Actions.persist_credentials(credentials_filename,
                                                    profile,
                                                    region,
                                                    token)

    @staticmethod
    def exec_with_credentials(region, command, token):
        env = os.environ.copy()

        env["AWS_ACCESS_KEY_ID"] = token.credentials.access_key
        env["AWS_SECRET_ACCESS_KEY"] = token.credentials.secret_key
        env["AWS_SESSION_TOKEN"] = token.credentials.session_token
        env["AWS_DEFAULT_REGION"] = region

        Popen(shlex.split(command),
              env=env,
              shell=False).wait()

    @staticmethod
    def exec_handler(region, exec_command, **kwargs):
        return lambda token: Actions.exec_with_credentials(region, exec_command, token)

    @staticmethod
    def saml_token(region, assertion, **kwargs):
        assertion = SamlAssertion(assertion)
        role = assertion.roles()[0]

        conn = boto.sts.connect_to_region(region, anon=True)
        return conn.assume_role_with_saml(role['role'], role['principle'],
                                          assertion.encode())

    @staticmethod
    def user_token(region, role_arn, session_name,
                   mfa_serial_number=None, mfa_token=None,
                   **kwargs):
        conn = boto.sts.connect_to_region(region)

        return conn.assume_role(role_arn, session_name,
                                mfa_serial_number=mfa_serial_number,
                                mfa_token=mfa_token)
