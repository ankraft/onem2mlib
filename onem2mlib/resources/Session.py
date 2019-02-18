#
#	Session.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for Session handling.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON


logger = logging.getLogger(__name__)

class Session:
	"""
	A Session object is used when connecting to a oneM2M CSE. It holds various information
	about the current session, such as the CSE endpoint, credentials, desired encoding, etc.
	"""

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
			`onem2mlib.constants.Encoding_JSON`. Providing a wrong encoding will throw a `onem2mlib.exceptions.NotSupportedError`
			exception.
		"""
		self.address = address
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """
		while self.address is not None and self.address.endswith('/'):
			self.address = self.address[:-1]

		self.originator = originator
		""" String. This specifies the originator for identification in access control policies. 
			It can be a domain, an originatorID, the string "all", or a role-ID. """

		self.encoding = encoding
		"""	Integer, either `onem2mlib.constants.Encoding_XML` or `onem2mlib.constants.Encoding_JSON`.
			It specifies the type of encoding for requests between the AE and the CSE. """
		if self.encoding not in [CON.Encoding_XML, CON.Encoding_JSON]:
			logger.critical('Unsupported encoding: ' + str(self.encoding))
			raise EXC.NotSupportedError('Unsupported encoding: ' + str(self.encoding))
		if self.encoding == CON.Encoding_XML and not CON.Support_XML:
			logger.critical('Unsupported encoding: Encoding_XML.')
			raise EXC.NotSupportedError('Unsupported encoding: Encoding_XML')
		if not self.originator:
			logger.error('Missing accessControlOriginator')
			raise EXC.AuthenticationError('Missing accessControlOriginator')


	def __str__(self):
		result = 'Session:\n'
		result += INT.strResource('address', None, self.address)
		result += INT.strResource('originator', None, self.originator)
		result += INT.strResource('encoding', None, self.encoding)
		return result

