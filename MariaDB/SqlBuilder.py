"""

 Class: SqlBuilder

 Python3 class for constructing specific portions of complex SQL statements. 
 Though this class can be instantiated, it is typically not as all methods are type @classmethod.


 Public methods:
  * sql_builder_SELECT(<table_name>, l_fields) -> STR:<sql-select-text> 
  * sql_builder_WHERE(d_where)                 -> DICT:{'prepare_values': l_vals, 'text': "<where-text>"}
  * sql_builder_JOIN(l_joins)                  -> STR:<sql-join-text>
  * sql_builder_ORDER(l_orderby)               -> STR:<sql-orderby-text>
  * sql_builder_GROUP(l_groupby)               -> STR:<sql-groupby-text>

 USAGE:  see TEST __main__ at bottom of file

"""

##----------------------------------------------------------------------------------------
import re
import sys

##----------------------------------------------------------------------------------------
class MethodInputError(Exception):
  pass

##----------------------------------------------------------------------------------------
class SqlBuilder():

  def __init__(self, d_init_args):

    ## class-name 
    self.cname = self.__class__.__name__

    ## "object" id (appended to by child class) 
    self.oid = self.cname
    if 'caller' in d_init_args:
      caller = d_init_args['caller']
      self.oid = "%s.%s" % (caller, self.cname)

    self.DEBUG = 0 
    if 'debug' in d_init_args: 
      self.DEBUG   = d_init_args['debug']

  #----------------------------------------------------------------------------- 
  @classmethod
  def sql_build_SELECT(cls, table_name, l_select):

    ##
    ## Builds the "SELECT ..." portion of an sql query "SELECT <select-list> from table"
    ## Return a text string
    ##

    if len(l_select) == 0:
      l_select = ['*']
    select_str = ",".join( l_select )

    text = "SELECT " + select_str + " FROM " + table_name
 
    return( text )
 
  #----------------------------------------------------------------------------- 
  @classmethod
  def sql_build_JOIN(cls, l_joins):

    ## Builds the "JOIN ..." portion of an sql query: "LEFTJOIN <jointable> ON (t1.id = t1.id), JOIN <j1> ON ...."
    ## Return a text string or None if no joins
    ##
    ##  l_joins = [
    ##             { "LEFT JOIN":  ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    ##             { "JOIN":       ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    ##             { "RIGHT JOIN": ["<join_to_table>", "<left_colname>", "<right_colname>" ] }
    ##           ]
    ##
    tag = "%s.sql_build_JOIN" % cls.__name__

    text = None   

    ## { "join": ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    if len(l_joins) > 0:
      l_join_statements = []
      join_str = None 
      for d_join in l_joins:
        for join_label,l_args in d_join.items():
          if (join_label != 'JOIN') and (join_label != 'LEFT JOIN') and (join_label != 'RIGHT JOIN'):
            raise MethodInputError("%s: Invalid JOIN-label syntax (%s)" % (tag, join_label))

          table = l_args[0]
          left_col = l_args[1]
          right_col = l_args[2]
          join_statement = join_label + ' ' + table + " ON (" + left_col + " = " + right_col + ")"
          l_join_statements.append(join_statement)
        text = " ".join( l_join_statements) 
 
    return( text )
 
  #----------------------------------------------------------------------------- 
  @classmethod
  def sql_build_WHERE(cls, d_where):
    ## 
    ## Builds the "WHERE ..." portion of an sql query: "WHERE <k1> = <v1> AND <k1> = <v2> ...."
    ## and the actual WHERE text string (or None if no where clause to be used) 
    ## WHERE clause key/value pairs are passed in d_where.
    ## Values can be "NULL", "!NULL" or comma-sep-list, and will get translated to approprate sql.
    ## Numerical values preceeded by (>, <, >=, <=)  will get translated to approprate sql.
    ##
    ## To pass complex/grouped WHERE logic, use d_where['_COMPLEX_WHERE_'] = <complex-sql-statement> 
    ## This statement text does NOT include the word "WHERE"!! 
    ## Example: 
    ##   d_where['_COMPLEX_WHERE_'] = "(k1 = 'b' AND k2 = 'c') OR (j1 = 'b' AND j2 = 'c')"
    ##
    ## Returns a dict containing "WHERE ..." text as a formatting string and a list of values 
    ## to associated with the formatting string.  
    ## 
    
    tag = "%s.sql_build_WHERE" % cls.__name__

    text = None   
    l_vals = []
     
    if len(d_where.keys()):
      ##print("WHERE: %s", % (d_where)) 
      complex_where_sql = None
      if '_COMPLEX_WHERE_' in d_where:
        complex_where_sql = d_where['_COMPLEX_WHERE_']
        del d_where['_COMPLEX_WHERE_']
 
      where_str = None 
      l_where = []
      for k,v in d_where.items():

        ## NULL or !NULL
        if v == 'NULL':
          l_where.append( k + " IS NULL" ) 
          ## do not append "v" to l_vals

        elif v == '!NULL':
          l_where.append( k + " IS NOT NULL" ) 
          ## do not append "v" to l_vals

        else:
          ## comma-sep-list
          m = re.match(",", str(v))
          if m:
            l_where.append( k + " IN (" + """%s""" + ")" ) 
            l_vals.append( v ) 

          else:
            ## identify assignment-operator
            op = '=' ## default operator is '='
            ## check for numerical operators
            m = re.match( "^([\>\<]=?)(\d.*)$", str(v))
            if m:
              op = m.group(1)
              v = m.group(2)
              if cls.get_str_numeric_type(v): 
                v = cls.cast_str_numeric_type(v) 
            l_where.append( k + " " + op + " " + """%s""" ) 
            l_vals.append( v ) 

      ## add complex where logic statement if exists
      if complex_where_sql:
        l_where.append(complex_where_sql) 

      ## Join all the where pairs (including the complex segement) with AND logic
      text = " AND ".join( l_where )

    d_where_results = { 'prepare_values': l_vals, 'text': text }

    return( d_where_results )

  #----------------------------------------------------------------------------- 
  @classmethod
  def sql_build_ORDER(cls, l_orderby):

    ## Builds the "ORDER BY ..." portion of an sql query: "ORDER BY <k1> ASC, <k2> DESC ...."
    ## Return a text string or None if no joins
    ##    
    ## l_orderby syntax: 
    ##  l_orderby = [ {"col1": "<desc|asc>" }, ... {"colN": "<desc|asc>" } ]
    ##
    text = None   

    sep = ", " ## comma separated joining of multiple column sorts
 
    if len(l_orderby) > 0:
      l_order_statements = []
      for d_orderby in l_orderby:
        for col,direction in d_orderby.items():
          order_statement =  "%s %s" % (col, direction)
          l_order_statements.append(order_statement)

      text = "ORDER BY " + sep.join(l_order_statements) 

    return( text )

  #----------------------------------------------------------------------------- 
  @classmethod
  def sql_build_GROUP(cls, l_groupby):

    ## Builds the "GROUP BY ..." portion of an sql query: "GROUP BY <k1>[, <k2> ....]"
    ## Return a text string or None if no joins
    ##    
    ## l_groupby syntax: 
    ##  l_groupby = [ "col1", "col2", ... ]
    ##
    text = None   
 
    sep = "," ## comma separated joining of multiple column grouping 

    if len(l_groupby) > 0:
      text = "GROUP BY " + sep.join(l_groupby) 

    return( text )

  #------------------------------------------------------------------------
  @classmethod
  def get_str_numeric_type(cls, str):
    """ 
    Identify the numeric type of a number which has been cast in string from.
    Example: Suppose we have the string "3.03". We don't want to know the
            obvious - that it is actually type=string, we want to know what
            numeric type (INT or FLOAT) is contained in this string.
    Return: Numeric data-type. Returns None if string is not a number (ether INT or FLOAT)
    """ 
    numeric_type = None
    m = re.match("^(\d+)$", str)
    if m:
      numeric_type = 'int'
    else:
      m = re.match("^(\d+\.\d+)$", str)
      if m:
        numeric_type = 'float'

    return(numeric_type)

  #------------------------------------------------------------------------
  @classmethod
  def cast_str_numeric_type(cls, str):
    """ 
     Identify the numeric type of a number which has been cast in string from
     and cast it to the appropriate numeric type.
     Example: Suppose we have the string "3.03". We need to identify that the
            numeric-type is a float and cast it as a float. Same logic for int.
     Return: Number appropriately casted to its type. Returns None if string is not a number (ether INT or FLOAT)
    """ 
    casted_number = None
    m = re.match("^(\d+)$", str)
    if m:
      casted_number = int(str)
    else:
      m = re.match("^(\d+\.\d+)$", str)
      if m:
        casted_number = float(str)

    return(casted_number)

  #------------------------------------------------------------------------
  def __dataDump(cls, data, title=None):
    ## Mimic Perl's data Dumper()
    if title is None:
      title = 'DataDump'
    print("--START: %s-----------------" % (title) )
    print(data)
    print("--END-----------------------" )

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  myname = 'sqlbuilder_test'

  print("%s: Test Start..." % (myname))

  text_select = SqlBuilder.sql_build_SELECT("my_table", ['name','addess','phone'])
  print("> SELECT: %s" % (text_select))

  text_where = SqlBuilder.sql_build_WHERE({'firstname': 'bill', 'lastname': 'fanselow'})
  print("> WHERE: %s" % (text_where))

  text_join = SqlBuilder.sql_build_JOIN( [ {'LEFT JOIN': ['join_table', 'left_col', 'right_col'] } ] )
  print("> JOINS: %s" % (text_join))

  text_orderby = SqlBuilder.sql_build_ORDER( [ {"col1": "desc" }, {"col2": "asc" } ] )
  print("> ORDER-BY: %s" % (text_orderby))
 
  text_groupby = SqlBuilder.sql_build_GROUP( [ "col1", "col2" ] )
  print("> GROUP-BY: %s" % (text_groupby))

  print("%s: Test END" % (myname))

  sys.exit(1) 
