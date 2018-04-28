===========================
How to contribute to Qingmi
===========================
Thanks for considering contributing to Qingmi.


Running the testsuite
=====================

You probably want to set up a virtualenv or virtualenvwrapper.

The minimal requirement for running the testsuite is `py.test`. You can install it with:

    pip install pytest

For a more isolated test environment, you can also install `tox` instead of
`pytest`. You can install it with::

    pip install tox

The `tox` command will then run all tests against multiple combinations of
Python versions and dependency versions.