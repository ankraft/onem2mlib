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
import onem2mlib.constants as CON



class Session:
	""" The Session class is used when connecting to a oneM2M CSE."""
	#def __init__(self, address=None,  username=None, password=None, originator=None):
	def __init__(self, address,  originator, encoding=CON.Encoding_JSON):
		"""
		Initialize a Session object. 

		Please note, the credentials (the originator) are currently hold unsecured in
		Session instances.

		Args:

		- *address*: String. The URL of the CSE host to connect to. This includes the protocol, hostname, 
			port number, and any API prefix etc.
		- *originator*: String. The originator for identification in access control policies.
		- *encoding*: Integer. The encoding of request content. Optional, the default is
			*onem2mlib.constants.Encoding_JSON*. Providing a wrong encoding will throw a *NotSupportedError*
			exception.
		"""
		self.address = address
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """

		self.originator = originator
		""" String. This specifies the originator for identification in access control policies. 
			It can be a domain, an originatorID, the string "all", or a role-ID. """

		self.encoding = encoding
		"""	Integer, either *onem2mlib.constants.Encoding_XML* or *onem2mlib.constants.Encoding_JSON*.
			It specifies the type of encoding for requests between the AE and the CSE. """
		if self.encoding not in [CON.Encoding_XML, CON.Encoding_JSON]:
			raise EXC.NotSupportedError('Unsupported encoding: ' + str(self.encoding))

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
