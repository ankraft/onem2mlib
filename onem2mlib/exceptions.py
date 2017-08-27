#
#	exceptions.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines the exceptions used in various modules.
#

"""
This sub-module defines the exceptions used in the onem2mlib module.
"""


class OneM2MLibError(Exception):
    """Base class for exceptions in this module."""
    pass

class CSEOperationError(OneM2MLibError):
    """Exception raised for errors when invoking operations on the CSE.
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """

class ParameterError(OneM2MLibError):
    """Exception raised for errors in paramterization of resource classes. 
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """
