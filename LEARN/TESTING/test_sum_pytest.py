import pytest

def sum_method(obj):
  return(sum(obj))

def test_sum_list():
    assert sum_method([1, 2, 3]) == 6, "Should be 6"

def test_sum_tuple():
#    assert sum((1, 2, 2)) == 6, "Should be 6"
    assert sum_method((1, 2, 2)) == 6, "Should be 6"

def test_sum_NAN():
   with pytest.raises(TypeError):
      sum([1, 2, 'bad']) 
