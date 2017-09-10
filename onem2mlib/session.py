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

import onem2mlib.internal as INT
import onem2mlib.exceptions as EXC



class Session:
	""" The Session class is used when connecting to a oneM2M CSE."""
	#def __init__(self, address=None,  username=None, password=None, originator=None):
	def __init__(self, address,  originator):
		"""
		Initialize a Session object. 

		Please note, the credentials (the originator) are currently hold unsecured in
		Session instances.

		Args:

		- *address*: String. The URL of the CSE host to connect to. This includes the protocol, hostname, 
			port number, and any API prefix etc.
		- *originator*: String. The originator for identification in access control policies
		"""
		self.address = address
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """
		self.originator = originator
		""" String. This specifies the originator for identification in access control policies. 
			It can be a domain, an originatorID, the string "all", or a role-ID. """
		self.connected = False
		""" Boolean. This flag indicates whether the session is successfully connected to a CSE. """

		if not self.originator:
			raise EXC.AuthenticationError('Missing accessControlOriginator.')


	def __str__(self):
		result = 'Session:\n'
		result += INT.strResource('address', None, self.address)
		result += INT.strResource('originator', None, self.originator)
		result += INT.strResource('connected', None, self.connected)
		return result
