"""

  Demonstrating how to call methods useing their (string) name.
  We use the getattr() function to get the value of a named attribute of an object.

  How getattr() works:

    ...
    class Person:
        age = 23
        name = "Adam"

    person = Person()
    print('The age is:', getattr(person, "age"))
    print('The age is:', person.age)
    ...

  It can also be used to get the value of a method.
  method = getattr(object, method_name)
  Calling the method is then done simply by appending parens to the returned value: method() 

"""
method_names = ['bar1', 'bar2']

class Foo:
    def bar1(self):
        print('bar1')
    def bar2(self):
        print('bar2')

    def callall(self):
        # Here, we use "self" for our first arg to getattr()
        print("Calling from inside class...")
        for mname in method_names: 
            f = getattr(self, mname)
            f()
   

if __name__ == '__main__':

    f = Foo()
    f.callall()

    print("\n\nCalling from outside class...")
    # Here, we have to instantiate the class for our first arg to getattr()
    for mname in method_names: 
        getattr(f, mname)()

