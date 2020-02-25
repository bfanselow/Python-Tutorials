import pytest

from BankAccount import BankAccount

@pytest.fixture
def minimum_balance():
   """Return the minimum account balance"""
   min_balance = BankAccount.MINIMUM_BALANCE
   return( min_balance ) 

@pytest.fixture
def open_minimum_account():
   """Open a BankAccount with minimum initial balance"""
   min_bal = BankAccount.MINIMUM_BALANCE
   my_min_account = BankAccount(min_bal) 
   return( my_min_account ) 

@pytest.fixture
def open_large_account():
   """Open a BankAccount with large initial balance"""
   my_large_account = BankAccount(1000) 
   return( my_large_account ) 
