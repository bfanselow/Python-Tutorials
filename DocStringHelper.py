"""
  This module provides a hands-on example of docstring use.
  Docstrings make for good code commenting, but are also useful for producing formatted help text.
  We use the Google style of docstings

  Test it using the following:
    1) module-level help
       python
       >> import DocStringHelper as dsh
       >> help(dsh)
       OR
       >> dsh.__doc__

    2) class-level help
       python
       >> from DocStringHelper import SampleClass
       >> help(SampleClass)

    3) method-level help
       python
       >> from DocStringHelper import SampleClass
       >> help(SampleClass.doubler)
"""

class SampleClass(object):

    """
    The class is a useless class for demonstrating docstring usage

    Init-Args:
        arg (str): Arg is used for...
        *args:     Variable arguments are used for...
        **kwargs:  Keyword arguments are used for...

    Attributes:
        text (str): Store some useless text initialization data
    """

    def __init__(self, arg, *args, **kwargs):
        self.text = arg

    def doubler(self, N_input ):
        """This is a simple class method to demonstrate method docstrings
        Args:
            N_input (int): A useless integer input
        Raises:
            ValueError: Input must be an integer
        Returns:
            N_output: (int) 2*N_input
        """

        if not isinstance(N_input, int):
          raise ValueError("Input must be an integer")

        N_output = 2*N_input
        return(N_output)
