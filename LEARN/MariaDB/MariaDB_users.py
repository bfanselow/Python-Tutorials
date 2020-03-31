"""

 Class: MariaDB_users()
 Subclass of MariaDB()

 Python3 MariaDB() class for "users" database table 
 
 USAGE: see TEST __main__ at bottom of file

  MariaDB [dbname]> describe users;
  +------------------+--------------+------+-----+---------+----------------+
  | Field            | Type         | Null | Key | Default | Extra          |
  +------------------+--------------+------+-----+---------+----------------+
  | id               | int(11)      | NO   | PRI | NULL    | auto_increment |
  | username         | varchar(32)  | NO   | UNI | NULL    |                |
  | fullname         | varchar(64)  | NO   |     | NULL    |                |
  | password_hash    | varchar(255) | YES  |     | NULL    |                |
  | api_key          | text         | YES  |     | NULL    |                |
  | email            | varchar(256) | NO   |     | NULL    |                |
  | is_authenticated | bool         | NO   |     | 0       |                |
  | is_admin         | bool         | NO   |     | 0       |                |
  | ts_created       | datetime     | NO   |     | NULL    |                |
  | ts_last_login    | datetime     | NO   |     | NULL    |                |
  +------------------+--------------+------+-----+---------+----------------+
 
"""
import datetime
import logging
import sys

## custom libs
from MariaDB import MariaDB

##----------------------------------------------------------------------------------------

REQ_COLUMN_NAMES = {
  "users":
    [ 
      "username",
      "fullname",
      "password_hash",
      "api_key",
      "email"
    ]
}

##-----------------------------------------------------------------------------
class MariaDB_users(MariaDB):
  
  def __init__(self, d_init_args):
    
    ## Call parent __init__()
    ## Sets: cname, oid
    super(self.__class__, self).__init__(d_init_args)

    self.db_name = "sars" 
    self.req_col_names = REQ_COLUMN_NAMES 


  #-----------------------------------------------------------------------------
  def get_all_users(self, d_args=None):
    ##
    ## Return all user records 
    ##

    tag = self.cname + '.get_all_users'

    if d_args is None:
      d_args = {}

    table_name = "users"

    d_args['dataonly'] = 1

    d_data = None
    try:    
      d_data = self.getAllRecords(table_name, d_args)
    except Exception as e:
      raise

    return( d_data )

  #-----------------------------------------------------------------------------
  def get_user_by_username(self, username, d_args=None):
    ##
    ## Return user record for passed username 
    ##

    tag = self.cname + '.get_user_by_username'

    if d_args is None:
      d_args = {}

    table_name = "users"

    d_where = {'username': username}
    
    d_args['dataonly'] = 1
    d_args['validate'] = 0 

    d_data = None
    try:    
      d_data = self.getSingleRecord(table_name, d_where, d_args)
    except Exception as e:
      raise

    return( d_data )

  #-----------------------------------------------------------------------------
  def get_user_by_email(self, email, d_args=None):
    ##
    ## Return user record for passed email 
    ##

    tag = self.cname + '.get_user_by_email'

    if d_args is None:
      d_args = {}

    table_name = "users"

    d_where = {'email': email}
    
    d_args['dataonly'] = 1
    d_args['validate'] = 0 

    d_data = None
    try:    
      d_data = self.getSingleRecord(table_name, d_where, d_args)
    except Exception as e:
      raise

    return( d_data )

  #-----------------------------------------------------------------------------
  def update_user_by_username(self, username, d_updates, d_args=None):
    ##
    ## Update user record for passed username 
    ##

    tag = self.cname + '.update_user_by_username'

    if d_args is None:
      d_args = {}

    table_name = "users"

    d_where = {'username': username}
    
    d_args['dataonly'] = 1
    d_args['validate'] = 1 

    rows = 0 
    try:    
      rows = self.update_single_record(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise

    return( rows )

  #-----------------------------------------------------------------------------
  def get_groups_for_username(self, username, d_args=None):
    ##
    ## Return groups for passed username 
    ##

    tag = self.cname + '.get_groups_for_username'

    if d_args is None:
      d_args = {}

    table_name = "users"

    d_where = {'username': username}
    d_args['select'] = "groupname" 
    
    d_args['join'] = [ 
      {"INNER JOIN": ["user_group_map", "user_group_map.FK_user_id", "users.id" ]}, 
      {"INNER JOIN": ["groups", "groups.group_id", "user_group_map.FK_group_id" ]} 
    ]

    d_args['dataonly'] = 1
    d_args['validate'] = 1

    d_data = None
    try:    
      d_data = self.getRecordsWhere(table_name, d_where, d_args)
    except Exception as e:
      raise

    return( d_data )

  #-----------------------------------------------------------------------------
  def new_user(self, d_record, d_args=None):
    ##
    ## Insert a new "users" record
    ## Return database id
    ##

    tag = self.cname + '.new_user'

    if not d_args:
      d_args = {}

    table_name = "users"

    format = "%Y-%m-%d %H:%M:%S"
    o_dt = datetime.datetime.now()
    ts_now = o_dt.strftime(format) 

    if 'ts_created' not in d_record:
      d_record['ts_created'] = ts_now

    req_col_names = self.req_col_names[table_name]

    valid = 1
    for key in req_col_names:
      if key not in d_record:
        valid = 0
        err_msg = "%s: Missing required column input data: [%s]" % (tag, key)
        self._log("ERROR", err_msg)
        raise MissingAttributeError(err_msg)
        break
      else:
        value = d_record[key]
        if value is None:
          value = ''
          if value == '':
            err_msg = "%s: NULL required column input data: [%s]" % (tag, key)
            self._log("ERROR", err_msg)
            raise MissingAttributeError(err_msg)

    username = d_record['username']
    self._log("INFO", "%s: Inserting new record for username=[%s]..." % (tag, username))

    db_id = None
    if valid:
      try:
        db_id = self.submit_single_record(table_name, d_record, d_args)
      except Exception as e:
        self._log("ERROR", "%s: submit_single_record failed with exception: %s" % (tag, e))
        raise

    if db_id == None:
      self._log("ERROR", "%s: Failed to insert new record: [%s]" % (tag, str(d_record)))

    return( db_id )

 
##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":
 
  import traceback
 
  myname = 'mdb_users_tester'

  DB_ARGS = {
    'host': 'localhost',
    'database': 'sars',
    'user': 'sars_admin',
    'password':   '**********'
  }

  ## create simple STDOUT logger
  logger = logging.getLogger(__name__)
  stdout_h = logging.StreamHandler(sys.stdout)
  stdout_h.setFormatter(logging.Formatter('%(asctime)s  %(name)s   %(levelname)s:  %(message)s'))
  logger.addHandler(stdout_h)
  logger.setLevel(logging.DEBUG)

  d_init_args = { 'db_args': DB_ARGS, 'logger': logger, 'persist': 0 }

  ## Instantiate MariaDB_users
  logger.info("Instantiating MariaDB_users()...")
  try:
    db_h = MariaDB_users(d_init_args)
  except Exception as e:
    print("%s: MariaDB_users.init() failed with exception: %s" % (myname, e))
    sys.exit(1) 

  username = "wfanselow" 
  logger.debug("Getting user-record for: %s" % (username))
  with db_h:
    try:
      d_data = db_h.get_user_by_username(username)
    except Exception as e:
      tb = traceback.format_exc() 
      print("%s: MariaDB_users().get_user_by_username(%s) failed with exception:\n%s" % (myname, username, tb))
      sys.exit(1) 

    if d_data:
      print("%s: User-record for: %s: %s" % (myname, username, d_data))
    else:
      print("%s: No records retrieved for user: [%s]" % (myname, username))
