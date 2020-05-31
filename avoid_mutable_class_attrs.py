#!/usr/bin/env python3

"""
  Simple demonstration of the importance of NOT using mutable
  objects as Class attributes.  Using mutable class attributes is
  very dangerous, because they belong to the class definition
  rather than the instance. Therefore it is easy to accidentally mutate
  state across multiple instances of the same class.
"""

class Band(object):

  members = set()   ## BAD! set() is mutable and belongs to all instances of Class

  def __init__(self, band_name):
    self.bandname = band_name

  def add_member(self, name):
    self.members.add(name)

  def __repr__(self):
    return("%s: %s" % (self.bandname, self.members))




if __name__ == '__main__':
  print("Creating new band. Should have no members")
  band1 = Band('Jokers')
  print( band1 )

  name = 'Bill'
  print("Adding member to new band: [%s]" % (name))
  band1.add_member(name)
  print( band1 )


  print("\nCreating another band...")
  band2 = Band('Moosenuts')
  print( band2 ) ## Whoa! We already have "Bill" in this new band!

  name = 'Joe'
  print("Adding member to new band: [%s]" % (name))
  band2.add_member(name)
  print( band2 )
  print( band1 ) ## Whoa! "Joe" is in both bands now!
