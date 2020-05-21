"""

  char_matching.py

  Problem:
   Write an algormithm that takes the list of cities and groups together any that
   have the exact same character set in the name (regradless of char order).

  Example:
   INPUT: 
     cities = ['Tokyo', 'London', 'Rome', 'Donlon', 'Kyoto', 'Paris']

   OUTPUT: 
    [
      [ 'Tokyo', 'Kyoto' ],
      [ 'London', 'Donlon' ],
      [ 'Rome' ],
      ['Paris' ]
    ]

"""

cities = ['Tokyo', 'London', 'Rome', 'Donlon', 'Kyoto', 'Paris']

def lower_split(word):
  lword = word.lower()
  chars = [char for char in lword]
  return(chars)

def create_char_set_map(l_strings):
  """ 
   map strings to their respective char set
   return a tuple: (sets, d_city_char_sets)
  """ 
  sets = []
  d_city_char_sets = {}
  for city in cities:
    char_set = set(lower_split(city))
    d_city_char_sets[city] = char_set
    if char_set not in sets:
      sets.append(char_set)
  return (sets, d_city_char_sets) 


print(cities)  
sets,d_city_char_sets = create_char_set_map(cities)

l_city_set_matches = []
for char_set in sets:
  l_cities_with_char_set = []
  ## see which cities have this char-set
  for c,s in d_city_char_sets.items():
    ##print("CITY=%s, SET=%s" % (c,s))
    if s == char_set:
      l_cities_with_char_set.append(c)
  l_city_set_matches.append(l_cities_with_char_set)

print(l_city_set_matches)  
