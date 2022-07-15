import pytest

"""
 Demonstrate paramterized fixtures.

 Automatically, run all tests which use the "timeline" fixure multiple times with different inputs.
 For each iteration of the tests the request.param value can be used as input to test resources.

 Usage:
 $ pytest -v pytest_parameterization.py

 This will run the test_timeline() test 3 times each with different input. The first two
 iterations of the test will fail (since one of the 3 values in the passed tuple fails assertion).
 The third iteration will succeed (since all 3 values in the tuple pass assertion).

"""
class TimeLine:
    def __init__(self, instances=[0, 0, 0]):
        self.instances = instances


@pytest.fixture(params=[
    [1, 2, 3], [2, 4, 5], [6, 8, 10]
])
def timeline(request):
    return TimeLine(request.param)


def test_timeline(timeline):
    for instance in timeline.instances:
        print(f"+ timeline={timeline}   instance={instance}")
        assert instance % 2 == 0
