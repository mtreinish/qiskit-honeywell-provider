# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Test Decorators."""

import functools
import os
import unittest

from qiskit.providers.honeywell.credentials import discover_credentials
from qiskit.providers.honeywell import exceptions
from qiskit.util import _has_connection

HAS_NET_CONNECTION = None


def online_test(func):
    """Decorator that signals that the test uses the network (and the online API):

    It involves:
        * determines if the test should be skipped by checking environment
            variables.
        * if the `USE_ALTERNATE_ENV_CREDENTIALS` environment variable is
          set, it reads the credentials from an alternative set of environment
          variables.
        * if the test is not skipped, it reads `qe_token` and `qe_url` from
            `Qconfig.py`, environment variables or qiskitrc.
        * if the test is not skipped, it appends `qe_token` and `qe_url` as
            arguments to the test function.

    Args:
        func (callable): test function to be decorated.

    Returns:
        callable: the decorated function.
    """

    @functools.wraps(func)
    def _wrapper(self, *args, **kwargs):
        # To avoid checking the connection in each test
        global HAS_NET_CONNECTION  # pylint: disable=global-statement

        if os.getenv('QISKIT_TEST_SKIP_ONLINE'):
            raise unittest.SkipTest('Skipping online tests')

        if HAS_NET_CONNECTION is None:
            HAS_NET_CONNECTION = _has_connection('qapi.honeywell.com', 443)

        if not HAS_NET_CONNECTION:
            raise unittest.SkipTest("Test requires internet connection.")

        try:
            credentials = discover_credentials()
        except exceptions.HoneywellError:
            raise unittest.SkipTest("Test requires valid honeywell credentials")
        if not credentials:
            raise unittest.SkipTest("Test requires honeywell credentials")

        return func(self, *args, **kwargs)

    return _wrapper