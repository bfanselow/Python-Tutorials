### Fun with list-comprehension

**Given a list of numbers, drop the first and last 33% of the list**
```
>>> numbers = range(100)
>>> [x for x in numbers][1+len(numbers)//3:-(len(numbers)//3)+1]
[34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66,67]
