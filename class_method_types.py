class TestClass():
    """ Demonstration of the various methods types found in a python Class"""

    class_data = {"data-scope": "class"}

    def __init__(self, init_data):
        print("\nINITIALIZING...")
        self.instance_data = init_data

    def instance_method(self):
        """ Can only be called on instance of TestClass(). Has access to class and instance attributes """
        print(">>instance_method")
        print(self.class_data)
        print(self.instance_data)

    @classmethod
    def class_method(cls):
        """ Can be called on either TestClass class, i.e. TestClass.class_method(). Has access only to class attributes """
        print(">>class_method (no instance attrs)")
        print(cls.class_data)

    @staticmethod
    def static_method():
        """ Can be called on either TestClass class for TestClass() instance. Has no access to class or instance attributes """
        print(">>static_method (no instance or class attrs)")

    def regular_method():
        """ Can only be called on either TestClass class. Has no access to class or instance attributes.
         (Seems identicial to static_method() but cannot be called on instance)
         
        """
        print(">>regular_method (no instance or class attrs)")


if __name__ == '__main__':

    TestClass.static_method()
    TestClass.class_method()
    TestClass.regular_method()
    
    # Calling TestClass.instance_method() raises TypeError
    # >>> TestClass.instance_method()
    # Traceback (most recent call last):
    # File "<stdin>", line 1, in <module>
    # TypeError: instance_method() missing 1 required positional argument: 'self'

    tc = TestClass( {"data-scope": "instance"} )
    tc.instance_method()
    tc.class_method()
    tc.static_method()
    
    # Calling tc.regular_method raise TypeError
    # >>> tc = TestClass()
    # >>> tc.regular_method()
    # Traceback (most recent call last):
    # File "<stdin>", line 1, in <module>
    # TypeError: regular_method() takes 0 positional arguments but 1 was given
