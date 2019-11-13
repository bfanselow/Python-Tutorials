"""

  File: ClassWithConstantAttr.py
  class-name: ClassWithConstantAttr()
  Author: Bill Fanselow
  Date: 11-10-2019
  
  Description:

  This class demonstrates some of the ways to "hide" class attributes in Python,
  or make them CONSTANT, so that they cannot be viewed but not modified.

  In many languages, one can specify class attributes of type "protected" 
  and "private". Protected means that a class and its subclasses have access 
  to the variable, but any other classes need to use a getter/setter to do 
  anything with the variable. Private means that only that class has direct 
  access to the variable, everything else needs a method/function to access 
  or change that data. In Python, there are no "protected/private" types. 

  In Python the convention is to use a single _ prefix on attribute names to 
  mean "protected" and a __ prefix (double-underscore) to mean "private". 
  Python mangles the names of variables like "__foo" so that they're not easily
  visible to code outside the class that contains them, although you can get around 
  it if you're determined enough (use "<obj>._<className>__var" as shown below).

  The best way to enforce that the class attribute not be modified/deleted,
  you can use the @property decorator as demonstrated below. 

  TEST: Execute the Class.main() 
  # python3 ClassWithConstantAttr.py 

"""

class ClassWithConstantAttr():
      
    _class_protected_var = "Not supposed to change me but you can" 
    __class_private_var = "Also, not supposed to change me. Try it " 

    def __init__(self, d_init_args ):
      self.cname = self.__class__.__name__       
      print("  +%s: Class initialized with init-args: %s" % (self.cname, str(d_init_args)))
   
      self.public_attr = "init:I-am-public" 
      self._protected_attr_in_init = "init:Not supposed to change me but you can" 
      self.__private_attr_in_init = "init:Also, not supposed to change me. Try it" 
      
      print("  +%s: Original value of self._protected_attr_in_init: %s" % (self.cname, self._protected_attr_in_init))
      print("  +%s: Original value of self.__private_attr_in_init: %s" % (self.cname, self.__private_attr_in_init))

      if 'setme' in d_init_args:
        set_val = d_init_args['setme']
        self._protected_attr_in_init = set_val 
        print("  +%s: New value of self._protected_attr_in_init: %s" % (self.cname, self._protected_attr_in_init))
        self.__private_attr_in_init = set_val 
        print("  +%s: New value of self.__private_attr_in_init: %s" % (self.cname, self.__private_attr_in_init))

    def getAttr(self, attr_name):
      if hasattr(self, attr_name):
        value = getattr(self, attr_name)
        print("  +%s: Accessing self.%s" % (self.cname, attr_name))
        return(value)
      else:
        raise AttributeError("%s: Class has no attr: %s" % (self.cname, attr_name)) 

    def setAttr(self, attr_name, value):
      if hasattr(self,attr_name):
        print("  +%s: Setting self.%s to new value=[%s]" % (self.cname, attr_name, value))
        setattr(self, attr_name, value)
      else:
        raise AttributeError("%s: Class has no attr: %s" % (self.cname, attr_name)) 

    @property
    def SOME_CONST(self):
      val = "I cannot be changed"
      return( val )

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  print("\n\nStart of class test") 
  try:
    my_obj = ClassWithConstantAttr( {'setme': 'I am changing you on init'} )
  except Exception as e:
    print("Class-init failed with exception: %s" (e)) 
    raise

  print("\n==================================") 
  print("Let's try to change some class attrs by direct access...") 

  ## Direct access to (and modification of) "_class_protected_var" will work!
  print(" \nTEST 1: Direct access to: _class_protected_var") 
  print(" BEFORE: _class_protected_var=[%s]" % my_obj._class_protected_var) 
  my_obj._class_protected_var = "Changed by direct attr access" 
  print(" AFTER: _class_protected_var=[%s]" % my_obj._class_protected_var) 

  ## Direct access to "__class_private_var" will not work - an exception will be raised
  print(" \nTEST 2: Direct access to: __class_private_var") 
  try:
    print(" BEFORE: __class_private_var=[%s]" % my_obj.__class_private_var) 
    my_obj.__class_private_var = "Changed by direct attr access" 
  except AttributeError as e:
    print(" >>>>>>EXCEPTION TRAPPED: %s" % (e)) 
  finally:
    print(" WARNING: __class_private_var was NOT changed due to lack of external direct access") 

  ## Direct access to (and modification of) "_protected_attr_in_init" will work!
  print(" \nTEST 3: Direct access to: _protected_attr_in_init") 
  print(" BEFORE: _protected_attr_in_init=[%s]" % my_obj._protected_attr_in_init) 
  my_obj._protected_attr_in_init = "Changed by direct attr access" 
  print(" AFTER: _protected_attr_in_init=[%s]" % my_obj._protected_attr_in_init) 

  ## Direct access to "__private_attr_in_init" will not work - an exception will be raised
  print(" \nTEST 4: Direct access to: __private_attr_in_init") 
  try:
    print(" BEFORE: __private_attr_in_init=[%s]" % my_obj.__private_attr_in_init) 
    my_obj.__private_attr_in_init = "Changed by direct attr access" 
  except AttributeError as e:
    print(" >>>>>>EXCEPTION TRAPPED: %s" % (e)) 
  finally:
    print(" WARNING: __private_attr_in_init was NOT changed due to lack of external direct access") 

  ## Cheater access to "__private_attr_in_init" will work - you now now the masked name of private attrs! 
  print(" \nTEST 4a: Cheater-direct access to: __private_attr_in_init using: x._ClassWithConstantAttr__private_attr_in_init") 
  val = my_obj._ClassWithConstantAttr__private_attr_in_init 
  print(" BEFORE (cheater): x._ClassWithConstantAttr__private_attr_in_init=[%s]" % val) 
  my_obj._ClassWithConstantAttr__private_attr_in_init = "I was changed by a cheater!" 
  val = my_obj._ClassWithConstantAttr__private_attr_in_init 
  print(" AFTER (cheater): x._ClassWithConstantAttr__private_attr_in_init=[%s]" % val) 

  ## Direct access to SOME_CONST is allowed, buty NOT modfication! - an exception will be raised
  print(" \nTEST 5: Direct access to: __private_attr_in_init") 
  try:
    print(" BEFORE: SOME_CONST=[%s]" % my_obj.SOME_CONST) 
    my_obj.SOME_CONST = "Trying to change this by direct attr access" 
  except AttributeError as e:
    print(" >>>>>>EXCEPTION TRAPPED: %s" % (e)) 
  finally:
    print(" WARNING: SOME_CONST was NOT changed due to lack of external direct access") 

  print("\n==================================") 
  print("Now let's try to access and modify some class attrs by getAttr(), setAttr() methods...") 
  
  ## getAttr(public_attr) will work
  print(" \nTEST 6: getAttr(): public_attr") 
  val = my_obj.getAttr('public_attr') 
  print(" VALUE: [%s]" % val) 
  ## setAttr(public_attr) will work
  print(" \nTEST 7: setAttr(): public_attr") 
  my_obj.setAttr('public_attr', 'Changed with setAttr() method') 
  val = my_obj.getAttr('public_attr') 
  print(" VALUE: [%s]" % val) 
  
  ## getAttr(_protected_attr_in_init) will work
  print(" \nTEST 8: getAttr(): _protected_attr_in_init") 
  val = my_obj.getAttr('_protected_attr_in_init') 
  print(" VALUE: [%s]" % val) 
  ## setAttr(_protected_attr_in_init) will work
  print(" \nTEST 9: setAttr(): _protected_attr_in_init") 
  my_obj.setAttr('_protected_attr_in_init', 'Changed with setAttr() method') 
  val = my_obj.getAttr('_protected_attr_in_init') 
  print(" VALUE: [%s]" % val) 

  ## getAttr(__private_attr_in_init) will NOT work
  print(" \nTEST 10: getattr(): __private_attr_in_init") 
  try:
    val = getattr(my_obj, '__private_attr_in_init') 
    print(" VALUE: [%s]" % val) 
  except AttributeError as e:
    print(" >>>>>>EXCEPTION TRAPPED: %s" % (e)) 
  finally:
    print(" WARNING: __private_attr_in_init could not be access via getattr()") 


  print(" \nTEST 11: getAttr(): __private_attr_in_init") 
  try:
    val = my_obj.getAttr('__private_attr_in_init') 
    print(" VALUE: [%s]" % val) 
  except AttributeError as e:
    print(" >>>>>>EXCEPTION TRAPPED: %s" % (e)) 
  finally:
    print(" WARNING: __private_attr_in_init could not be access via getAttr()") 

  ##
  ## It is obvious now that setAttr(__private_attr_in_init) will NOT work
  ##

  ## getattr(SOME_CONST) and getAttr(SOME_CONST) will work
  print(" \nTEST 12: getattr(): SOME_CONST ") 
  val = getattr(my_obj, 'SOME_CONST') 
  print(" VALUE: [%s]" % val) 
  print(" \nTEST 13: getAttr(): SOME_CONST ") 
  val = my_obj.getAttr('SOME_CONST') 
  print(" VALUE: [%s]" % val) 

  print(" \nTEST 14: setAttr(): SOME_CONST") 
  try:
    val = my_obj.setAttr('SOME_CONST', "Changed with setAttr() method") 
    print(" VALUE: [%s]" % val) 
  except AttributeError as e:
    print(" >>>>>>EXCEPTION TRAPPED: %s" % (e)) 
  finally:
    print(" WARNING: SOME_CONST could not be changed via setAttr()") 
  
  print("\nEnd class test\n\n") 
