# Code Challenges
#### Ansers at bottom of page

---

### 1) With the following two expressions
#### a) Compare the output of each
```
>>> dict([(i,x*x) for i,x in enumerate(range(1,7), start=1)])
...
>>> [{i:x*x} for i,x in enumerate(range(1,7), start=1)]
...
```
#### b) Transform the output of each one into the output of the other

---

### 2)
#### a) Construct a 4x4 dim matrix with incrementing values from 1-16
```
m = [[ 1,  2,  3,  4], [ 5,  6,  7,  8], [ 9, 10, 11, 12], [13, 14, 15, 16]]
# visualize with numpy
>>> np.asarray(m)
array([[ 1,  2,  3,  4],
       [ 5,  6,  7,  8],
       [ 9, 10, 11, 12],
       [13, 14, 15, 16]])
```
#### b) Find an expression for, and display the top-right and bottom-left 2x2 sub-matrices
```
>>>np.asarray(topright)
array([[ 3,  4],
       [ 7,  8]])
...
>>>np.asarray(bottomleft)
array([[ 9,  10],
       [ 13,  14]])
```

---
# Answers:
###  1a)
```
>>> dict([(i,x*x) for i,x in enumerate(range(1,7), start=1)])
{1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36}
...
>>> [{i:x*x} for i,x in enumerate(range(1,7), start=1)]
[{1: 1}, {2: 4}, {3: 9}, {4: 16}, {5: 25}, {6: 36}]
...
```
### 1b)
```
>>> l = dict([(i,x*x) for i,x in enumerate(range(1,7), start=1)])
>>> l
[(1, 1), (2, 4), (3, 9), (4, 16), (5, 25), (6, 36)]
>>> [{t[0]: t[1]} for t in l]
[{1: 1}, {2: 4}, {3: 9}, {4: 16}, {5: 25}, {6: 36}]
...
...
...
>>> l = [{i:x*x} for i,x in enumerate(range(1,7), start=1)]
>>> l
[{1: 1}, {2: 4}, {3: 9}, {4: 16}, {5: 25}, {6: 36}]
>>> [ list(d.items())[0] for d in l]
[(1, 1), (2, 4), (3, 9), (4, 16), (5, 25), (6, 36)]
# OR
>>> [ next(iter(d.items())) for d in l]
[(1, 1), (2, 4), (3, 9), (4, 16), (5, 25), (6, 36)]
```

---

### 2a)
```
>>> m = [ [j for j in range(i,i+4)] for i in range(1,17,4)]
>>> m
[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
>>> import numpy as np
>>> np.asarray(m)
array([[ 1,  2,  3,  4],
       [ 5,  6,  7,  8],
       [ 9, 10, 11, 12],
       [13, 14, 15, 16]])
```
 ### 2b) Top-right
```
>>> tr = [ l[2:] for l in m[:2]]
>>> np.asarray(tr)
array([[3, 4],
       [7, 8]])

```
###  2b) Bottom-left
>>> bl = [ l[:2] for l in m[2:]]
>>> bl
[[9, 10], [13, 14]]
>>> np.asarray(bl)
array([[ 9, 10],
       [13, 14]])
```
