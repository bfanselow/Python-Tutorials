"""

  File: utils_object.py
  Author: Bill Fanselow
  
  Description:
    Object (dict|list) manipulation functions 

"""

myname = 'utils_object.py'

DEBUG = 2

#------------------------------------------------------------------------
class MethodInputError(Exception):
  pass

##===========================================================================
def is_dict_subset(d_superset, d_subset):
  """
   Check to see if one dict (d_subset) is a subset of another dict (d_superset).
   Retrun True if subset, False otherwise.
  """
  myname = 'is_dict_subset'

  if not isinstance(d_superset, dict):
    raise MethodInputError("%s: Both input args must be type=dict" % myname)
  if not isinstance(d_subset, dict):
    raise MethodInputError("%s: Both input args must be type=dict" % myname)

  for key, value in d_subset.items():
    if key not in d_superset:
      return False 

    if isinstance(value, dict):
      if not is_dict_subset(d_superset[key], value):
        return False 

    elif isinstance(value, str):
      if value not in d_superset[key]:
        return False 

    elif isinstance(value, list):
      if not set(value) <= set(d_superset[key]):
        return False 

    elif isinstance(value, set):
      if not value <= d_superset[key]:
        return False 

    else:
      if not value == d_superset[key]:
        return False 

  return True

##===========================================================================
def is_list_subset(l_superset, l_subset):
  """
   Check to see if one list (l_subset) is a subset of another list (l_superset).
   (order does not matter)
   Retrun True if subset, False otherwise.
  """
  myname = 'is_list_subset'
  
  if not isinstance(l_superset, list):
    raise MethodInputError("%s: Both input args must be type=list" % myname)
  if not isinstance(l_subset, list):
    raise MethodInputError("%s: Both input args must be type=list" % myname)

  if(set(l_subset).issubset(set(l_superset))): 
    return True 
  else:
    return False
      
#------------------------------------------------------------------------
# MAIN()
#------------------------------------------------------------------------
if __name__ == "__main__":
 
    d_pattern = {
            'a': 'hello world',
            'b': 12345,
            'c': 1.2345,
            'd': [1, 2, 3, 4, 5],
            'e': {1, 2, 3, 4, 5},
            'f': {
                'a': 'hello world',
                'b': 12345,
                'c': 1.2345,
                'd': [1, 2, 3, 4, 5],
                'e': {1, 2, 3, 4, 5},
                'g': False,
                'h': None
            },
            'g': False,
            'h': None,
            'question': 'mcve',
            'metadata': {}
    }

    ###########################################
    ## TEST: is_dict_subset()
    ###########################################
    print("\n--------------------------------")
    print("TEST is_dict_subset():")
    print("Pattern: %s\n" % (d_pattern))
    d1 = {'a': 'hello world'}
    print("Is dict subset: %s" % (d1))
    print( is_dict_subset(d_pattern, d1) ) 
    d2 = {'f': {
            'b': 12345,
            'c': 1.2345,
            'e': { 2, 3, 5},
         }
    }
    print("Is dict subset: %s" % (d2))
    print( is_dict_subset(d_pattern, d2) ) 
    d3 = { 'e': { 2, 3, 6} }
    print("Is dict subset: %s" % (d3))
    print( is_dict_subset(d_pattern, d3) ) 
    #d4 = 'string-test' 
    #print("Is dict subset: %s" % (d4))
    #print( is_dict_subset(d_pattern, d4) ) 

    d5 = {"kvmproto2.idc1.level3.com":{"stderr":"","pid":0,"retcode":0,"stdout":"The directory /app/java already exists!!! Please remove the /app/java symlink if you would like the latest JDK installed"}}
    d_pattern = {'kvmproto2.idc1.level3.com': {'retcode': 0}}
    print("Is dict subset: %s" % (d5))
    print( is_dict_subset(d_pattern, d5) ) 

    ###########################################
    ## TEST: is_list_subset()
    ###########################################
    print("\n--------------------------------")
    l_pattern = [9, 4, 5, 8, 10] 
    print("TEST is_list_subset()")
    print ("Pattern : " + str(l_pattern)) 
    l_ss1 = [10, 5] 
    print("Is list subset: %s" % (l_ss1))
    print( is_list_subset(l_pattern, l_ss1) ) 
    l_ss2 = [10, 5, 3] 
    print("Is list subset: %s" % (l_ss2))
    print( is_list_subset(l_pattern, l_ss2) ) 
    #d3 = { 'e': { 2, 3, 6} }
    #print("Is list subset: %s" % (d3))
    #print( is_list_subset(l_pattern, d3) ) 
    
    ###########################################
    ## TEST: foo()
    ###########################################
    # print("\n--------------------------------")
