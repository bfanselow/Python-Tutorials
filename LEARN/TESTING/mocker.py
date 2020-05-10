"""

 Simple test of pytest-mock

 Requires pip-install pytest-mock

 Usage: python3 -m pytest -v mocker.py

"""

import pytest

def regular_sum(a, b):
    return a + b


def test_sum_1(mocker):
    mocker.patch(__name__ + ".regular_sum", return_value=9)
    assert regular_sum(2, 3) == 9


def test_sum_2(mocker):
    def mocked_sum(a, b):
        return( b + b )

    mocker.patch(__name__ + ".regular_sum", side_effect=mocked_sum)
    assert regular_sum(2, 3) == 6
