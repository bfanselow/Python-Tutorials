# create the database
  $ sudo mysql -p < db_create.mysql

# (re)create all of the tables 
  $ sudo ./init_tables.sh

# (re)create all of the users 
  $ sudo mysql -p < db_users_grants.mysql
