#!/usr/bin/env python3
"""

  File: pandas_dataframe.py
  Description:
    Simple testing of Pandas DataFrame concepts
    See below for expected output.

  Bill Fanselow
  11-05-2019

"""

import pandas as pd

sep = "\n----------------------------------------------------"

d_data = {'name': ["Bill", "Joe", "Bob"], 'age': [15,16,17], 'weight': [120, 127, 130]}
df = pd.DataFrame(d_data)

print("Simple DF\n%s%s" % (df, sep))

df_c = df[['age']]
print("Single column of DF (age)\n%s%s\n" % (df_c, sep))

df_mc = df[['name','age']]
print("Multi column of DF (name, age)\n%s%s" % (df_mc, sep))

d_row = {'name': "Steve", 'age': 15, 'weight': 122}
df.append(d_row, ignore_index=True)
print("Appended new row (%s)\n%s%s" % (d_row, df, sep))

df['AxW'] = df['age'] * df['weight']
print("New column with formula (age*weight)\n%s%s" % (df, sep))

df_row = df.loc[2]
print("Select single row (df.loc[2])\n%s%s" % (df_row, sep))

df_rows = df[0:2]
print("Select row slice (df[1:2])\n%s%s" % (df_rows, sep))

df.rename(index={0:'a', 1:'b', 2:'c'})
print("Rename rows indeces (nums to letters)\n%s%s" % (df, sep))

df.rename(columns={'name':'fname', 'AxW':'prod-AW'}, inplace=True)
print("Rename columns (name=>fname, AxW=>prod-AW)\n%s%s" % (df, sep))


"""

 Running this script will produce the following:


Simple DF
   age  name  weight
0   15  Bill     120
1   16   Joe     127
2   17   Bob     130

[3 rows x 3 columns]
----------------------------------------------------
Single column of DF (age)
   age
0   15
1   16
2   17

[3 rows x 1 columns]
----------------------------------------------------

Multi column of DF (name, age)
   name  age
0  Bill   15
1   Joe   16
2   Bob   17

[3 rows x 2 columns]
----------------------------------------------------
Appended new row ({'age': 15, 'weight': 122, 'name': 'Steve'})
   age  name  weight
0   15  Bill     120
1   16   Joe     127
2   17   Bob     130

[3 rows x 3 columns]
----------------------------------------------------
New column with formula (age*weight)
   age  name  weight   AxW
0   15  Bill     120  1800
1   16   Joe     127  2032
2   17   Bob     130  2210

[3 rows x 4 columns]
----------------------------------------------------
Select single row (df.loc[2])
age         17
name       Bob
weight     130
AxW       2210
Name: 2, dtype: object
----------------------------------------------------
Select row slice (df[1:2])
   age  name  weight   AxW
0   15  Bill     120  1800
1   16   Joe     127  2032

[2 rows x 4 columns]
----------------------------------------------------
Rename rows indeces (nums to letters)
   age  name  weight   AxW
0   15  Bill     120  1800
1   16   Joe     127  2032
2   17   Bob     130  2210

[3 rows x 4 columns]
----------------------------------------------------
Rename columns (name=>fname, AxW=>prod-AW)
   age fname  weight  prod-AW
0   15  Bill     120     1800
1   16   Joe     127     2032
2   17   Bob     130     2210

[3 rows x 4 columns]

"""
