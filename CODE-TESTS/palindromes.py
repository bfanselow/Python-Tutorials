"""

  palindromes.py

  Given a paragraph of text, identify if there are any "palindromes"
  (words spelled the same forward or backword) not including single letter
  words

  Simple palindrome examples: civic, radar, level, rotor, kayak, reviver, racecar, madam, refer

"""
import re

text = "Once upon a time, I paddeled a kayak to up the Northwest passage. I had no GPS but did occasionally did refer to a map. At one point during the trip a large motor boat almost hit me, which could have shredded me to bits with its rotor spinning like a forumla-1 racecar."

def clean_text(in_string):
  """
   Remove commas, periods and other punctuation
   Throw out any one-letter words
  """
  cleaned_str = re.sub('[,\.\!\?\:\;\(\)]', '', in_string)
  cleaned_str = re.sub('\s\w\s', '', cleaned_str)

  return cleaned_str

plist = [word for word in  clean_text(text).split() if  word == word[::-1] ]
print( plist )
