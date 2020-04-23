"""

  Controller methods

"""

def check_login(name,pw):
  status = False
  if name == pw:
    status = True
  return( status )

