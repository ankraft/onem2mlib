#
#	session.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines the session class.
#

"""
This sub-module defines the Session class used in the onem2mlib module.
"""

import onem2mlib.utilities as UT



class Session:
	""" The Session class is used when connecting to a oneM2M CSE."""
	def __init__(self, address=None, username=None, password=None):
		"""
		Initialize a Session object. 

		Please note, the credentials are currently hold unsecured in Session instances.

		Args:

		- *address*: The URL of the CSE host to connect to. This includes the protocol, hostname, 
			port number, and any API prefix etc.
		- *username*: The username part of the credentials.
		- *password*: The password part of the credentials.  
		"""
		self.address = address
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """
		self.username = username
		""" String. The username part of the credentials. """
		self.password = password
		""" String. The password part of the credentials. """
		self.connected = False
		""" Boolean. This flag indicates whether the session is successfully connected to a CSE. """


	def __str__(self):
		result = 'Session:\n'
		result += UT.strResource('address', None, self.address)
		result += UT.strResource('username', None, self.username)
		result += UT.strResource('password', None, self.password)
		result += UT.strResource('connected', None, self.connected)
		return result
