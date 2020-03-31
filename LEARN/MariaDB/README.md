# Python MariaDB/Mysql access 

## MariaDB.py
Top-level connection and generic SQL methods. Provides configurable connection persistence.

## MariaDB_users.py
Example of MariaDB_\<table\>.py class which provides SQL methods for a specific table.

## SqlBuilder.py 
Translate generic pseudo-query logic to actual SQL text. Used by MariaDB.py. 

## User.py 
This provides an ORM into MariaDB_users.py methods. I personally tend to avoid ORM's when I can, but when you need to use an ORM (such as is highly conventient for Flask user-management), this class is an example.

## mysql/ 
Collection of scripts for creating, initializing and refreshing group of related tables

