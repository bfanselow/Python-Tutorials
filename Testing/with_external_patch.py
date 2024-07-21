# Suppose we need to mock an external call the is used in an imported module

from stdlib_mock_test import my_isfile

def test_with_external_patch():
  object_path = "stdlib_mock_test.os.path.isfile"
  with patch(object_path, return_value="Yes")
      assert(my_isfile('foo/bar') == "Yes")
