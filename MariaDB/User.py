"""

  This class is used to instantiate "User" objects which are
  essentially an ORM to the MariaDb_users database.

  We instantiate a User() object by passing either the *email* or
  *username* properties of the user. Initialization will perform the
  database lookup of the user (based on the passed property) and
  build the User() with all properties. 

  Requirements: 
   * ./MariaDB_users.py
   * ./MariaDB.py


"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import logging 
import datetime
import time
import uuid

from MariaDB_users import MariaDB_users

##-----------------------------------------------------------------------------
class InitError(Exception):
  pass

##-----------------------------------------------------------------------------
class UserError(Exception):
  pass

##-----------------------------------------------------------------------------
class UserStorageError(Exception):
  pass

##-----------------------------------------------------------------------------
class User():

  def __init__(self, d_init_args, d_user_data):

    ## class-name
    self.cname = self.__class__.__name__

    if not d_init_args:
      raise InitError("%s: Missing init args: %s" % (self.cname))

    ## User properties
    self.user_props = [ 
      'username',
      'fullname',
      'email',
      'password_hash', 
      'api_key',
      'is_admin',
      'is_authenticated',
      'ts_created',
      'ts_last_login'
    ]
    ## User properties required for creation of new User
    self.new_user_props = ['username', 'fullname', 'email']

    self.username = None
    self.fullname = None
    self.email = None
    self.password_hash = None
    self.api_key = None
    self.is_admin = 0 
    self.is_authenticated = 0 
    self.ts_last_login = 0 

    ## Python logger
    self.logger = None
    if 'logger' not in d_init_args:
      raise InitError("%s: Missing required init arg: [logger]" % (self.cname))
    self.logger = d_init_args['logger']

    ## MariaDB connection handler
    self.dbch = None
    if 'conn_handle' not in d_init_args:
      raise InitError("%s: Missing required init arg: [conn_handle]" % (self.cname))
    self.dbch = d_init_args['conn_handle']

    ## Instantiate new MariaDB handler 
    DBH = None
    try:
      DBH = MariaDB_users( {'logger': self.logger, 'conn_handle': self.dbch} )
    except Exception as e:
      raise InitError("%s: MariaDB_users.init() failed with exception: %s" % (self.cname, e))
    self.DBH = DBH

    if 'new' in d_init_args:
      ## New User (needs be created)
      try:
        self = self.create_user(d_user_data)
      except Exception as e:
        raise InitError("%s: create_user() failed with exception: %s" % (self.cname, e))
    else:
      ## Existing User (query and build)
      try:
        self = self.get_user(d_user_data)
      except Exception as e:
        raise InitError("%s: get_user() failed with exception: %s" % (self.cname, e))

  #----------------------------------------------------------------------------
  def __repr__(self):
    """Object representation"""
    return '<User {}>'.format(self.username)

  #----------------------------------------------------------------------------
  def __bool__(self):
    """Object truth test"""
    if self.username:
      return True
    else:
      return False 

  #----------------------------------------------------------------------------
  def get_user(self, d_data):
    """
      Query for user from storage, and build User object.
      Return User object. Must return None (rather than raise Exception) if user does not exist!
    """
    search_key = 'username'
    if 'username' in d_data:
      username = d_data['username']
      search_val = username
      d_user = self.__get_by_username(username)
    else:
      raise UserError("%s: Cannot retrieve user based on input data: [%s]" % (self.cname, str(d_data)))

    if d_user:
      ## Build User object from data
      for prop in self.user_props:
        if prop not in d_user:
          raise UserError("%s: Required User property (%s) not found for %s=[%s]" % (self.cname,prop,search_key,search_val))
        value = d_user[prop]
        setattr(self, prop, value)
    else:
      self = None

    return(self)

  #----------------------------------------------------------------------------
  def create_user(self, d_user_data):
    """ 
       Create a new User object from passed data.
       Return User object. 
    """
    
    username = d_user_data['username']
    password = d_user_data['password']
    
    for prop in self.new_user_props:
      if prop not in d_user_data:
        raise UserError("%s: Required User property not found: [%s]" % (self.cname, prop))
      value = d_user_data[prop]
      setattr(self, prop, value)

    self.password_hash = self.generate_password(password)
    self.api_key = self.create_api_key(username)
   
    o_dt = datetime.datetime.now()
    self.ts_created = o_dt.strftime("%Y-%m-%d %H:%M:%S")
 
    try: 
      record_id = self.__store_user()
    except Exception as e:
      raise UserStorageError("%s: __store_user(%s) failed with exception: %s" % (self.cname, username, e))

    if not record_id:
      raise UserError("%s: Failed to create new user: %s" % (self.cname, username))

    return(self)

  #----------------------------------------------------------------------------
  def __store_user(self):
    """
      Store data for a new user object. 
      Return user data
    """

    d_user_data = {}
    for prop in self.user_props:
      if prop:
        d_user_data[prop] = getattr(self, prop)

    record_id = None 
    try:
      record_id = self.DBH.new_record(d_user_data)
    except Exception as e:
      raise UserStorageError("%s: MariaDB_users.new_record() failed with exception: %s" % (self.cname, e))

    return(record_id)

  #----------------------------------------------------------------------------
  def __get_by_username(self, username):
    """
      Query database to get user record from user username.
      No exception if user is not found! - simply returns None which will be handled by caller.
    """

    d_user = None
    try:
      d_user = self.DBH.get_user_by_username(username)
    except Exception as e:
      raise UserStorageError("%s: MariaDB_users.get_user_by_username(%s) failed with exception: %s" % (self.cname, username, e))

    return(d_user)

  #----------------------------------------------------------------------------
  def __update_user(self, d_user_data):
    """
      Internal method to update user-data changes to storage.
    """
    username = self.username

    for k,v in d_user_data.items():
      if hasattr(self, k):
        d_user_data[k] = v
        setattr(self, k, v)

    try:
      rows = self.DBH.update_user_by_username(username, d_user_data)
    except Exception as e:
      raise UserStorageError("%s: MariaDB_users.update_user_by_username(%s) failed with exception: %s" % (self.cname, username, e))

    if rows != 1: 
      raise UserError("%s: Failed to update user record for username=[%s]" % (self.cname, username))

    return(self)

  #----------------------------------------------------------------------------
  def is_active(self):
    """
      Required for Flask-Login: Always return true since ALL users are active
    """
    return True

  #----------------------------------------------------------------------------
  def is_anonymous(self):
    """
      Required for Flask-Login: Always return False since anonymous users are not supported
    """
    return False

  #----------------------------------------------------------------------------
  def is_authenticated(self):
    """
      Required for Flask-Login: Return True if user is authenticated
    """
    return self.is_authenticated 

  #----------------------------------------------------------------------------
  def get_id(self):
    """ 
     Required for Flask-Login: Return the User's *username*
    """ 
    return self.username

  #----------------------------------------------------------------------------
  def set_authenticated(self, **kwargs):
    """ 
      Set users authentication status to True 
    """

    o_dt = datetime.datetime.now()
    ts_now = o_dt.strftime("%Y-%m-%d %H:%M:%S")

    self.is_authenticated = True
    self.ts_last_login = ts_now 

    d_updates = {'is_authenticated': True}

    ## update ts_last_login by default (override with "login=0")
    login = 1
    if 'login' in kwargs:
      login = kwargs.get("login")
    if login:
      d_updates['ts_last_login'] = ts_now 

    try:
      self = self.__update_user(d_updates)
    except Exception as e:
     raise

    return(self)

  #----------------------------------------------------------------------------
  def unset_authenticated(self):
    """ 
      Set users authentication status to False 
    """
    self.is_authenticated = False 
    try:
      self = self.__update_user({'is_authenticated': False})
    except Exception as e:
     raise

    return(self)

  #----------------------------------------------------------------------------
  def public_data(self):
    """ 
      Return a dict of non-sensitive User attributes 
    """
    d_data = {
      'username':      self.username,
      'fullname':      self.fullname,
      'email':         self.email,
      'api_key':       self.api_key,
      'ts_created':    self.ts_created,
      'ts_last_login': self.ts_last_login
    } 
    return(d_data)

  #----------------------------------------------------------------------------
  def generate_password(self, password):
    """ 
      Generate and return password *hash* based on input password 
    """
    password_hash = generate_password_hash(password)
    return(password_hash) 

  #----------------------------------------------------------------------------
  def check_password(self, password):
    """ 
      Check input password against stored password hash 
    """
    return check_password_hash(self.password_hash, password)

  #----------------------------------------------------------------------------
  def create_api_key(self, username):
    """ 
      Generate and return an API-key 
    """
    id1 = uuid.uuid4()  
    id2 = uuid.uuid4()  
    timestamp = time.time()
    api_key = "%s.%s:%s.%s" % (id1,username,timestamp,id2)  
    return(api_key)

##-----------------------------------------------------------------------------
if __name__ == '__main__':

  import logging
  DB_ARGS = {
    'users': {
      'host':     'localhost',
      'database': 'sars',
      'user':     'admin',
      'password': '*********'
    }
  }
  logger = logging.getLogger('__name__')
  logger.setLevel(logging.DEBUG)

  l_usernames = ['wfanselow', 'bogus-user']

  for username in l_usernames: 
    d_init = {'logger': logger, 'storage_args': DB_ARGS}
    d_user = {'username': username}
    try:
      User = User(d_init, d_user) 
    except Exception as e:
      raise

    if User.username:
      print("User found: %s" % (username))
      print("%s\n" % (User.__dict__))
    else:
      print("ERROR - User not found with username: %s\n" % (username))
