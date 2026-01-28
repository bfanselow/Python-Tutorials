from contextlib import nullcontext as does_not_raise
import pytest
from pytest import raises


@pytest.mark.parametrize(
    ["x", "y", "expectation"],
    [
        (3, 2, does_not_raise()),
        (0, 1, does_not_raise()),
        (1, 0, raises(ZeroDivisionError)),
        (1, "0", raises(TypeError)),
    ],
)
def test_division(x, y, expectation):
    with expectation:
        x / y
