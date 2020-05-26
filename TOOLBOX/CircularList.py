"""
  TODO: still has a few bugs to cleanup. Needs more method input validation

  File: CircularList.py
  Class: CircList

  Implements a "circular" list which acts like a normal
  list, but whose with the special property that the next
  element after the "last" normal list element is the
  first element, so the start and end of the list are
  effectively adjacent.

  An index "pointer" keeps track of the current list index value,
  which allows for next() and previous() operations to traverse
  around the circular list.

  All Methods:
    * pop(idx=None):         standard list pop()
    * push(value=0):         push value onto start of list
    * insert(idx, value):    standard list insert()
    * pad(value=0, count=1): pad N values to end of list
    * append(value):         standard list append()
    * extend(new_list):      standard list extend()
    * remove(value):         standard list remove()
    * remove_all(value):     remove ALL of a particular value
    * uniq(keep=0):          return uniq values and optionally keep this as new list
    * clear():               clear the list to an empty list
    * sort(keep=0):          return sorted list and optional keep this as new list
    * reverse(keep=0):       return reversed list and optional keep this as new list
    * occurances(value):     count the occurances of a particular value
    * swap(idx1, idx2):      swap two values location at idx1 and idx2
    * reset():               return list to its original (initialized) value
    * index():               return value of current pointer
    * set_index(idx):        set new pointer value
    * move_index(count):     similar to set index but operates on +/- count from current pointer
    * this():                return value at index of current pointer
    * next(move=0):          return value at "next" index location, and optionally set this as new pointer
    * previous(move=0):      return value at "previous" index location, and optionally set this as new pointer

"""

DEBUG = 0

from collections import Counter
import copy

class CircList():

    def __init__(self, input_list=[], init_args=None):

        if not isinstance(input_list, list):
          raise ValueError("Init input must be of type=list")

        self.clist = input_list
        self.pointer = 0
        self.dtype = None
        if init_args:
          self.pointer = init_args.get('pointer', 0)
          self.dtype = init_args.get('dtype', None)

          if self.dtype is not None:
            self._check_values(input_list)

        self.original = copy.deepcopy(input_list)

    def __repr__(self):
        return str(self.clist)

    def pop(self, idx=None):
        """return the element at specified index and return"""
        if not self.clist:
          return None
        if idx:
          self._check_index(idx)
        else:
          idx = len(self.clist) - 1
        self._dprint("Popping value at index=[%s]" % (idx))
        return self.clist.pop(idx)

    def push(self, value=0):
        """insert value onto start of list"""
        self._dprint("Pushing value [%s] at index=[0]" % (value))
        if self.dtype is not None:
          self._check_values([value])
        self.clist.insert(0, value)

    def insert(self, idx, value):
        """regular insert operation"""
        self._check_index(idx)
        self._dprint("Adding value [%s] at index=[%s]" % (value, idx))
        if self.dtype is not None:
          self._check_values([value])
        self.clist.insert(idx, value)

    def pad(self, value=0, count=1):
        """pad <count> value(s) onto end of list"""
        self._dprint("Padding list with (%d) values [%s]" % (count, value))
        if self.dtype is not None:
          self._check_values([value])
        for i in range(count):
          self.clist.append(value)

    def append(self, value):
        """normal append operation"""
        self._dprint("Appending value [%s] to end of list" % (value))
        if self.dtype is not None:
          self._check_values([value])
        self.clist.append(value)

    def extend(self, new_list):
        """normal extend operation"""
        self._dprint("Extending list with values [%s]" % (value, str(new_list)))
        if self.dtype is not None:
          self._check_values(new_list)
        self.clist.extend(new_list)

    def remove(self, value):
        """remove first occurance of value"""
        self._dprint("Removing first occurance of value [%s]" % (value))
        self.clist.remove(value)

    def remove_all(self, value):
        """remove ALL occurances of value"""
        self._dprint("Removing all occurances of value [%s]" % (value))
        while value in self.clist:
          self.clist.remove(value)

    def uniq(self, keep=0):
        """ compute and return all unique elements in the set. If keep=1, set this uniq list to the new list """
        s = set()
        s.update(self.clist)
        if keep:
          self._dprint("Setting list to uniq version")
          self.clist = list(s)
        return list(s)

    def clear(self):
        """ Empty the list - setting the new list to []"""
        self._dprint("Clearing list")
        self.clist = []

    def sort(self, keep=0):
        """ sort and return the list. If keep=1, set this sorted list to the new list """
        slist = sorted(self.clist)
        if keep:
          self._dprint("Setting list to sorted version")
          self.clist = slist
        return slist

    def reverse(self, keep=0):
        """ reverse and return the list. If keep=1, set this reversed list to the new list """
        rlist = self.clist[::-1]
        if keep:
          self._dprint("Setting list to reversed version")
          self.clist = rlist
        return rlist

    def occurances(self, value):
        """ returns the count of a particular value """
        d_counts = Counter(self.cname)
        count = d_counts[value]
        return count

    def swap(self, idx1, idx2):
        """ swap two values based on a pair of indices """
        self._check_index(idx1)
        self._check_index(idx2)
        v1 = self.clist[idx1]
        v2 = self.clist[idx2]
        self._dprint("Swapping [%s] at [%d] with [%s] at [%d]" % (v1, idx1, v2, idx2))
        self.clist[idx1] = v2
        self.clist[idx2] = v1

    def reset(self):
        """ return list to its original form """
        self._dprint("Setting list back to original version")
        self.clist = self.original

    def this(self):
        """ return current element based on current pointer """
        if not self.clist:
          return None
        else:
          return self.clist[self.pointer]

    def next(self, move_pointer=0):
        """ return the next element based on current pointer, and optionally advance pointer """
        if not self.clist:
          return None
        else:
          pointer = self._pointer_forward(1, move_pointer)
          value = self.clist[pointer]
          return value

    def previous(self, move_pointer=0):
        """ return the previous element based on current pointer, and optionally decrement pointer """
        if not self.clist:
          return None
        else:
          pointer = self._pointer_backward(1, move_pointer)
          value = self.clist[pointer]
          return value

    def index(self):
        """ return current pointer """
        return self.pointer

    def set_index(self, idx):
        """ move current pointer to value idx"""
        if self.clist:
          self._check_index(idx)
          if idx >= len(self.clist):
            raise IndexError("New index must be less than or equal to list length (%d)" % (len(self.clist)))
          self._dprint("Setting pointer to [%d]" % (idx))
          self.pointer = idx

    def move_index(self, count):
        """ move current pointer in either direction by amount +-<count>"""
        if self.clist:
          if not isinstance(count, int):
            raise ValueError("Move count must be of type=int")
          if count > 0:
            self._pointer_forward(count, move=1)
          else:
            self._pointer_backward(count, move=1)

    def _dprint(self, msg, lvl=1):
      """ Internal debug printing"""
      if DEBUG >= lvl:
        print(msg)

    def _check_index(self, idx):
      """ Internal index check"""
      if not isinstance(idx, int):
        raise IndexError("Index must be of type=int")

    def _check_values(self, list_to_check):
      """ Internal value check"""
      for v in list_to_check:
         if not isinstance(v, self.dtype):
           dtype = type(v)
           raise ValueError("Cannot add value=(%s) type=(%s). All values must be of type=%s" % (v, dtype, self.dtype))

    def _pointer_backward(self, count, move=0):
      """
       Get new location of point based on a backward pointer move of count positions.
       Optionally set this as new pointer value.
      """
      if not self.clist:
        return None
      for i in range(count):
        if self.pointer == 0:
          pointer = len(self.clist) - 1
        else:
          pointer = self.pointer - 1
        if move:
          self._dprint("Decrementing pointer backward by %d to new value=[%d]" % (count, pointer))
          self.pointer = pointer
      return pointer

    def _pointer_forward(self, count, move=0):
      """
       Get new location of point based on a forward pointer move of count positions.
       Optionally set this as new pointer value.
      """
      if not self.clist:
        return None
      for i in range(count):
        if self.pointer == (len(self.clist) - 1): ## end of list
          pointer = 0
        else:
          pointer = self.pointer + 1
        if move:
          self._dprint("Advancing pointer forward by %d to new value=[%d]" % (count, pointer))
          self.pointer = pointer
        return pointer
