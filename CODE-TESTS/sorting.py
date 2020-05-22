"""
  
  sorting.py

  Problems:
   Given a page of text, perform the following sorting/counting
   1) count occurance of each word
   2) sort each word by length
   3) sort each word by first letter 
   4) sort each word by last letter 

"""
import re

page='Nory was a Catholic because her mother was a Catholic, and Nory’s mother was a Catholic because her father was a Catholic, and her father was a Catholic because his mother was a Catholic, or had been'

from collections import Counter

def text_to_wordlist(text):
  """ We cannot just split on whitespace, otherwise "Catholic" and "Catholic," will be treated as different words"""
  fmt_text = re.sub('[\.,\-\!]', ' ', text) ## remove end-of-word punctuation
  wordlist = fmt_text.split()
  #print(wordlist)
  return wordlist

def sort_by_length(text, reverse=True):
  wordlist = text_to_wordlist(text)
  new = sorted(wordlist, key=len, reverse=reverse) 
  return new

def sort_by_last_char(text):
  wordlist = text_to_wordlist(text)
  new = sorted(wordlist, key=lambda w: w[-1].lower()) 
  return new

def sort_by_first_char(text):
  wordlist = text_to_wordlist(text)
  new = sorted(wordlist, key=lambda w: w[0].lower()) 
  return new

def count_words(text):
  wordlist = text_to_wordlist(text)
  d_word_count = Counter(wordlist)
  return d_word_count

if __name__ == '__main__':
  d_count = count_words(page)
  print("WORD-COUNT\n%s" % d_count, end="\n\n")
  
  sorted_by_len = sort_by_length(page, reverse=True)
  print("SORT-BY-LENGTH\n%s" % sorted_by_len, end="\n\n")
  
  sorted_by_char1 = sort_by_first_char(page)
  print("SORT-BY-FIRST-CHAR\n%s" % sorted_by_char1, end="\n\n")
  
  sorted_by_charN = sort_by_last_char(page)
  print("SORT-BY-LAST-CHAR\n%s" % sorted_by_charN, end="\n\n")
