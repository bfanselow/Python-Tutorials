# Python MariaDB/Mysql access 

## MariaDB.py
Top-level db-connection handling and generic SQL methods. Provides configurable db-connection persistence.

## MariaDB_users.py
Example of MariaDB_\<table\>.py class which provides SQL methods for a specific table.

## SqlBuilder.py 
Translate generic pseudo-SQL logic into actual SQL text (used by MariaDB.py). 

## User.py 
I personally tend to avoid ORM's when I can, but there are a few times when an ORM is helpful (such as with the Flask user-management framework). This class provides an example of tying a **User** ORM into the MariaDB_users.py class.  

## mysql/ 
Collection of scripts for creating, initializing and refreshing a group of related tables.

