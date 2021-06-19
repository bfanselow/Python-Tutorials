"""
 Demonstrate how to call a method using its (string) name, via getattr()
"""

class Foo:
    def bar1(self):
        print('bar1')
    def bar2(self):
        print('bar2')



f = Foo()
getattr(f, "bar1")()

# OR

def call_method(o, name):
    return getattr(o, name)()
call_method(f, "bar2")

