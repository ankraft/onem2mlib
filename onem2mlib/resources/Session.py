#
#	Session.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for Session handling.
#

import logging
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA

logger = logging.getLogger(__name__)

class Session:
	"""
	A Session object is used when connecting to a oneM2M CSE. It holds various information
	about the current session, such as the CSE endpoint, credentials, desired encoding, etc.
	"""

	def __init__(self, address: str, originator: str, encoding: int = CON.Encoding_JSON):
		"""
		Initialize a Session object. 

		Args:
			address: The URL of the CSE host (e.g., http://localhost:8080).
			originator: The originator (ID) for identification.
			encoding: The encoding (JSON or XML).
		"""
		self.address = address.rstrip('/') if address else None
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """
		self.originator = originator
		""" String. This specifies the originator for identification in access control policies. 
			It can be a domain, an originatorID, the string "all", or a role-ID. """
		self.encoding = encoding
		"""	Integer, either `onem2mlib.constants.Encoding_XML` or `onem2mlib.constants.Encoding_JSON`.
			It specifies the type of encoding for requests between the AE and the CSE. """
		self.username = None
		""" String. The username for basic authentication, or the token string for bearer authentication. """
		self.password = None
		""" String. The password for basic authentication. If this is None, the username is treated 
			as a bearer token. """
		self.releaseVersion = '3'
		""" String. The oneM2M release version (e.g., "2a", "3", "4") used in the X-M2M-RVI header. """

		if not self.originator:
			logger.error('Missing originator for Session')
			raise EXC.AuthenticationError('Missing originator')

		if self.encoding not in [CON.Encoding_XML, CON.Encoding_JSON]:
			logger.critical(f'Unsupported encoding: {self.encoding}')
			raise EXC.NotSupportedError(f'Unsupported encoding: {self.encoding}')
		
		if self.encoding == CON.Encoding_XML and not CON.Support_XML:
			logger.critical('Unsupported encoding: Encoding_XML.')
			raise EXC.NotSupportedError('Unsupported encoding: Encoding_XML')

	def setUser(self, username: str, password: str|None = None) -> 'Session':
		""" 
		Set credentials for Basic Auth (user + pass) or 
		Bearer Auth (token only). 
		"""
		self.username = username
		self.password = password
		return self

	def setBearerToken(self, token: str) -> 'Session':
		""" Set a bearer token for the session. """
		return self.setUser(token, None)

	def setReleaseVersion(self, rvi: str) -> 'Session':
		""" Set the oneM2M release version (X-M2M-RVI). """
		self.releaseVersion = rvi
		return self

	def getCSEBase(self):
		"""
		Retrieves the CSEBase resource directly from the root path.
		Returns a populated CSEBase object.
		"""
  
		response = MCA.get(self, '-') 
		if response and response.status_code == 200:
			from .CSEBase import CSEBase
			resource = CSEBase(session=self, instantly=False)
			resource._parseResponse(response)
			return resource

		error_text = f"{response.status_code} - {response.text}" if response else "No response"
		logger.error(f'Retrieve CSEBase failed: {error_text}')
		raise EXC.CSEOperationError(f'Cannot get CSEBase. {error_text}')

	def __str__(self):
		result = 'Session:\n'
		result += INT.strResource('address', None, self.address)
		result += INT.strResource('originator', None, self.originator)
		result += INT.strResource('encoding', None, self.encoding)
		result += INT.strResource('rvi', None, self.releaseVersion)
		return result