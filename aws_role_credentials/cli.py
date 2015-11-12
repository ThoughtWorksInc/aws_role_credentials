#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
import logging

from os.path import expanduser
from aws_role_credentials import metadata
from aws_role_credentials.actions import Actions

log = logging.getLogger('aws_role_credentials')

def configurelogging():
    log.setLevel(logging.DEBUG)
    stderrlog = logging.StreamHandler()
    stderrlog.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(stderrlog)

def saml_action(args):
    assertion = ''
    try:
        assertion = ''.join([line for line in sys.stdin])
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass

    Actions(args.credentials_filename,
            args.profile,
            args.region).credentials_from_saml(assertion)

def user_action(args):
    Actions(args.credentials_filename,
            args.profile,
            args.region).credentials_from_user(args.role_arn,
                                               args.session_name)

def create_parser(prog, epilog,
                  actions):
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

    saml_parser = subparsers.add_parser('saml',
                                        description='Assume role using SAML assertion',
                                        parents=[parent_parser])

    saml_parser.set_defaults(func=actions['saml'])

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


    user_parser.set_defaults(func=actions['user'])


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

    arg_parser = create_parser(argv[0], epilog,
                               {'saml': saml_action,
                                'user': user_action})
    config = arg_parser.parse_args(args=argv[1:])

    log.info(epilog)

    config.credentials_filename = expanduser('~/.aws/credentials')

    config.func(config)

    return 0

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
