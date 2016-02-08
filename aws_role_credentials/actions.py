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
                 quiet,
                 **kwargs):

        self.credentials_filename = credentials_filename
        self.profile = profile
        self.region = region
        self.quiet = quiet

    @staticmethod
    def print_credentials(credentials_filename, profile, credentials):
        print '\n\n----------------------------------------------------------------'
        print 'Your credentials have been stored in the AWS configuration file {0} under the {1} profile.'.format(credentials_filename, profile)
        print 'Note that they will expire at {0}.'.format(credentials.expiration)
        print 'You may safely rerun this script at any time to refresh your credentials.'
        print 'To use this credential, call the AWS CLI with the --profile option (e.g. aws --profile {0} ec2 describe-instances).'.format(profile)
        print '----------------------------------------------------------------\n\n'

    @staticmethod
    def persist_credentials(credentials_filename,
                            profile, region, token, quiet, **kwargs):
        AwsCredentialsFile(credentials_filename).add_profile(profile,
                                                             region,
                                                             token.credentials)
        if not quiet:
            Actions.print_credentials(credentials_filename,
                                      profile,
                                      token.credentials)

    @staticmethod
    def credentials_handler(credentials_filename,
                            profile,
                            region, quiet, **kwargs):

        return lambda token: Actions.persist_credentials(credentials_filename,
                                                         profile,
                                                         region,
                                                         token,
                                                         quiet)

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
