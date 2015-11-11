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

def generate_credentials(credentials_filename,
                         profile,
                         region, assertion):

    Actions(credentials_filename, profile, region).credentials_from_saml(assertion)

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

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)

    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))

    config = arg_parser.parse_args(args=argv[1:])

    log.info(epilog)

    assertion = ''
    try:
        assertion = ''.join([line for line in sys.stdin])
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass

    generate_credentials(expanduser('~/.aws/credentials'),
                         'saml',
                         'us-east-1',
                         assertion)

    return 0

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
