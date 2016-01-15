#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
import logging
import os

from os.path import expanduser
from aws_role_credentials import metadata
from aws_role_credentials.actions import Actions

log = logging.getLogger('aws_role_credentials')


def configurelogging():
    log.setLevel(logging.DEBUG)
    stderrlog = logging.StreamHandler()
    stderrlog.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(stderrlog)


def read_stdin():
    try:
        return ''.join([line for line in sys.stdin])
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass


def token_action(args):
    if args['exec_command']:
        return Actions.exec_handler(**args)
    return Actions.credentials_handler(**args)


def saml_action(args):
    args['assertion'] = read_stdin()

    token_action(args)(Actions.saml_token(**args))


def user_action(args):
    token_action(args)(Actions.user_token(**args))


def create_parser(prog, epilog,
                  saml_action=saml_action,
                  user_action=user_action):
    arg_parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)
    subparsers = arg_parser.add_subparsers()

    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))

    parent_parser.add_argument(
        '--profile', type=str,
        default='sts',
        help='Use a specific profile in your credential file.')

    parent_parser.add_argument(
        '--region', type=str,
        default='us-east-1',
        help='The region to use. Overrides config/env settings.')

    parent_parser.add_argument(
        '--exec', type=str,
        dest='exec_command',
        help='If present then the string is read as a command to execute with the AWS credentials set as environment variables.')

    parent_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Do not print helpful info including token expiration on successful authentication.')

    saml_parser = subparsers.add_parser('saml',
                                        description='Assume role using SAML assertion',
                                        parents=[parent_parser])

    saml_parser.set_defaults(func=saml_action)

    user_parser = subparsers.add_parser('user',
                                        description='Assume role using IAM user',
                                        parents=[parent_parser])

    user_parser.add_argument(
        'role_arn', type=str,
        help='The arn of the role to assume',
    )

    user_parser.add_argument(
        'session_name', type=str,
        help='An identifier for the assumed role session.')

    user_parser.add_argument(
        '--mfa-serial-number', type=str,
        help='An identifier of the MFA device that is associated with the user.')

    user_parser.add_argument(
        '--mfa-token', type=str,
        help='The value provided by the MFA device.')

    user_parser.set_defaults(func=user_action)

    return arg_parser


def main(argv):
    configurelogging()

    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=metadata.project,
        version=metadata.version,
        authors='\n'.join(author_strings),
        url=metadata.url)

    arg_parser = create_parser(argv[0], epilog)
    config = arg_parser.parse_args(args=argv[1:])

    log.info(epilog)

    credentials_dir = expanduser('~/.aws')

    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)

    config.credentials_filename = os.path.join(credentials_dir, 'credentials')

    config.func(vars(config))

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
