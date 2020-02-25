"""

  File: BankAccount.py
  Class: BankAccount

  Description: 
   Simple example of bank account with methods for creating new account, depositing, and withdrawing.
   All account transactions must be done in integer amounts.

"""

##------------------------------------------------------------------------------------
##
## Class method Exceptions
##
class InvalidDollarAmount(Exception):
    pass
class BelowMinimumBalance(Exception):
    pass
class InsufficientAmount(Exception):
    pass
##------------------------------------------------------------------------------------
class BankAccount(object):

    MINIMUM_BALANCE = 10
    WITHDRAW_ALERT_AMOUNT = 1000

    @classmethod
    def validate_dollar_amount(cls, value): 
        """validate that input amount is a positive integer"""
        if not value:
            raise InvalidDollarAmount("Value must be a positive integer") 
        try: 
            int_val = int(value)
        except ValueError as e:
            raise InvalidDollarAmount("Value must be a positive integer") 
        if int_val <= 0:
            raise InvalidDollarAmount("Value must be a positive integer") 
        return(int_val) 

    def __init__(self, initial_balance=0):
        amount = BankAccount.validate_dollar_amount(initial_balance)
        if amount < BankAccount.MINIMUM_BALANCE:
            raise BelowMinimumBalance("Account requires minimum balance of: %d" % (BankAccount.MINIMUM_BALANCE))
        self.balance = amount 

    def withdraw(self, wd_amount):
        """Withdraw money from account"""
        amount = BankAccount.validate_dollar_amount(wd_amount)
        if self.balance < amount:
            raise InsufficientAmount("Insufficient funds available (%d) in account for withdraw of %d" % (self.balance,amount))
        if self.balance < BankAccount.MINIMUM_BALANCE:
            raise BelowMinimumBalance("Account requires minimum balance of: %d" % (BankAccount.MINIMUM_BALANCE))
        if amount > BankAccount.WITHDRAW_ALERT_AMOUNT:
            print("ALERT: Large account withdraw: %d" % (amount))
        self.balance -= amount

    def deposit(self, dep_amount):
        """Deposit money into account"""
        amount = BankAccount.validate_dollar_amount(dep_amount)
        self.balance += amount
