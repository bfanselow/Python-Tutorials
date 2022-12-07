"""
 Write a function to determine if a number is the same when reversed
"""

def palindrome_number(n):
    if int(''.join(list(str(n))[::-1])) == n:
        return True
    return False


if __name__ == '__main__':
  palindrome_number(12321)
  palindrome_number(12345)
