"""

 test_score_counts.py

 Problem: Given a list of names and the associated test score
          provide a count of each score value, with counts sorted
          hi to low 

"""

from collections import Counter
from collections import OrderedDict

def tally(list_scores):
  d_counts = dict(Counter(list_scores))

  sorted_counts = sorted(d_counts.items(), key=lambda x: x[1], reverse=True)

  return(OrderedDict(sorted_counts))




if __name__ == '__main__':

  scores = {
    'Doug Smith': 10,
    'Bill Smith': 10,
    'Bill Tingle': 9,
    'Joe Wright': 7,
    'Curt Block': 7,
    'Adam Hicks': 9,
    'Tony Shell': 5,
    'Gary Smits': 8,
    'Sam Spark': 10,
    'Coby Tuff': 8
  }
  print("SCORES\n%s" % (scores))
  print("TALLY\n")
  od = tally(scores.values())
  for k,v in od.items():
    print("%d: %d" % (k,v))
