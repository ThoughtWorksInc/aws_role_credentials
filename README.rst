===============================
AWS Role Credentials
===============================

.. image:: https://img.shields.io/pypi/v/aws_role_credentials.svg
        :target: https://pypi.python.org/pypi/aws_role_credentials

.. image:: https://snap-ci.com/ThoughtWorksInc/aws_role_credentials/branch/master/build_image
        :target: https://snap-ci.com/ThoughtWorksInc/aws_role_credentials/branch/master

Generates AWS credentials for roles using STS and writes them to ```~/.aws/credentials```

Usage
=====

Simply pipe a SAML assertion into awssaml

.. code-block:: shell

    # create credentials from saml assertion
    $ oktaauth -u jobloggs | aws_role_credentials saml --profile dev


Or for assuming a role using an IAM user:

.. code-block:: shell

    # create credentials from an iam user
    $ aws_role_credentials user \
      arn:aws:iam::111111:role/dev jobloggs-session \
      --profile dev

For roles that require MFA:

.. code-block:: shell

    # create credentials from an iam user with mfa
    $ aws_role_credentials user \
      arn:aws:iam::111111:role/dev jobloggs-session \
      --profile dev \
      --mfa-serial-number arn:aws:iam::111111:mfa/Jo \
      --mfa-token 102345

Transient mode
--------------

```aws_role_credentials``` also supports 'transient' mode where the
credentials are passed to a command as environment variables within
the process.  This adds an extra layer of safety and convinience.

To use transient mode simply pass a command to the ```--exec``` option
like so:

.. code-block:: shell

    # run 'aws s3 ls' with the generated role credentials from an iam user
    $ aws_role_credentials user \
      arn:aws:iam::111111:role/dev jobloggs-session \
      --exec 'aws s3 ls'


Options
=======

    --profile          Use a specific profile in your credential file (e.g. Development).  Defaults to sts.
    --region           The region to use. Overrides config/env settings.  Defaults to us-east-1.
    --exec             The command to execute with the AWS credentials

Thanks
======

Thanks to Quint Van Deman of AWS for demonstrating how to do this. https://blogs.aws.amazon.com/security/post/Tx1LDN0UBGJJ26Q/How-to-Implement-Federated-API-and-CLI-Access-Using-SAML-2-0-and-AD-FS


Authors
=======

* Peter Gillard-Moss
