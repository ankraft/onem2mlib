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
    """
    Base class for exceptions in this module.
    """
    pass


class CSEOperationError(OneM2MLibError):
    """
    Exception raised for errors when invoking operations on the CSE.
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """


class AuthenticationError(OneM2MLibError):
    """
    Exception raised for errors regarding authorization. 
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """


class ParameterError(OneM2MLibError):
    """
    Exception raised for errors in paramterization of resource classes. 
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """



class NotSupportedError(OneM2MLibError):
    """
    Exception raised when accessing/modifying not supported features of a resource.
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """



class EncodingError(OneM2MLibError):
    """
    Exception raised when receiving a wrong encoding.
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """


class ConfigurationError(OneM2MLibError):
    """
    Exception raised when encountering a missing or wrong configuration, e.g. of one
    if the library's components.
    """

    def __init__(self, message):
        self.message = message
        """ Explanation of the error. """

