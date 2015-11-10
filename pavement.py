# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

CODE_DIRECTORY='aws_role_credentials'

from paver.easy import task, consume_args

@task
@consume_args
def run(args):
    """Run the package's main script. All arguments are passed to it."""
    # The main script expects to get the called executable's name as
    # argv[0]. However, paver doesn't provide that in args. Even if it did (or
    # we dove into sys.argv), it wouldn't be useful because it would be paver's
    # executable. So we just pass the package name in as the executable name,
    # since it's close enough. This should never be seen by an end user
    # installing through Setuptools anyway.
    from aws_role_credentials.cli import main
    raise SystemExit(main([CODE_DIRECTORY] + args))
