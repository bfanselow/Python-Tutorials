"""
 File: test_bank_account.py

 Description:
  pytest testing of "BankAccount" class 

 Usage: python3 -m pytest -v

"""

import pytest
from BankAccount import BankAccount, InsufficientAmount, BelowMinimumBalance, InvalidDollarAmount

##------------------------------------------------------------------------
def test_exception_on_open_with_insufficient_amount():
    ## Test raise(InsufficientAmount) insufficient amount exception on account creation 
    with pytest.raises(BelowMinimumBalance):
        my_account = BankAccount(1) 

##------------------------------------------------------------------------
def test_exception_on_withdraw_insufficient_funds(minimum_balance):
    ## Test raise(InsufficientAmount) insufficient amount exception by withdraw() 
    ## when account does not have sufficient funds
    with pytest.raises(InsufficientAmount):
        my_account = BankAccount(minimum_balance) 
        my_account.withdraw(200)

##------------------------------------------------------------------------
## Parameterizing of a test is done to run the test against multiple sets of inputs
## and an expected output.
@pytest.mark.parametrize("dollar_amount", [ (0), (-20), ("twenty"), (""), ("*") ])
def test_exception_on_invalid_dollar_amount(dollar_amount):
    ## Test raise(InvalidDollarAmount) insufficient amount exception on dollar amounts 
    ## that are not positive integers 
    with pytest.raises(InvalidDollarAmount):
        my_account = BankAccount(dollar_amount) 

##------------------------------------------------------------------------
@pytest.mark.parametrize("input_amount, validated_amount", [ (10,10), ("20", 20) ])
def test_dollar_amount_validation(input_amount, validated_amount):
    assert validated_amount == BankAccount.validate_dollar_amount(input_amount)

##------------------------------------------------------------------------
@pytest.mark.parametrize("initial,earned,spent,expected", [
    (20, 30, 10, 40),
    (25, 20, 5, 40),
])
def test_transactions(initial, earned, spent, expected):
    ## Test deposit() and withdraw() methods for an account that was
    ## opened with zero balance
    my_account = BankAccount(initial)
    my_account.deposit(earned)
    my_account.withdraw(spent)
    assert my_account.balance == expected

