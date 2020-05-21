"""
  even_odd.py

  Problem:
   Given a list of ints, create a dict containg the number and a boolean
   for even|odd. Then do the same but sorted numerically 
"""

list = [3,7,4,1,7,9,0,2,4,6,10,12,5]

map_eo = map(lambda n: n%2 ==0, list)

print(list)
print(map_eo)

d_eo = dict(zip(list, map_eo))

print(d_eo)

